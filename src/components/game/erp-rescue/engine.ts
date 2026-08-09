/* ============================================================
   ERP RESCUE — Game engine (pure logic, DOM-free)
   Owns all state & rules. The view layer calls update(dt) each
   frame, reads `state`, and reacts to discrete events via hooks.
   ============================================================ */

import {
  MODULES, TUNING, activeTargetForWave, getRank,
  type Cell, type GameStatus, type GameSummary,
} from './types';

export interface EngineHooks {
  onFix?(p: { index: number; points: number; combo: number; critical: boolean; uptime: number }): void;
  onDown?(p: { index: number; uptime: number }): void;
  onMisclick?(p: { index: number; uptime: number }): void;
  onWaveUp?(p: { wave: number; perfect: boolean; bonus: number }): void;
  onSmartBomb?(p: { cleared: number }): void;
  onGameOver?(summary: GameSummary): void;
}

export interface EngineState {
  status: GameStatus;
  cells: Cell[];
  score: number;
  best: number;
  wave: number;
  combo: number;
  maxCombo: number;
  uptime: number;
  minUptime: number;
  elapsed: number;
}

export class RescueEngine {
  state: EngineState;
  private hooks: EngineHooks;
  private waveElapsed = 0;
  private spawnTimer = 0;
  private downsThisWave = 0;
  private smartBombUsed = false;
  private totalFixes = 0;
  private totalDowns = 0;

  constructor(hooks: EngineHooks = {}, best = 0) {
    this.hooks = hooks;
    this.state = this.freshState(best);
  }

  private freshState(best: number): EngineState {
    return {
      status: 'idle',
      cells: MODULES.map((def) => ({ def, status: 'idle', active: false, stress: 0, downTimer: 0 })),
      score: 0,
      best,
      wave: 1,
      combo: 0,
      maxCombo: 0,
      uptime: TUNING.startUptime,
      minUptime: TUNING.startUptime,
      elapsed: 0,
    };
  }

  /* ---- Lifecycle ---- */

  start(): void {
    const best = this.state.best;
    this.state = this.freshState(best);
    this.state.status = 'running';
    this.waveElapsed = 0;
    this.spawnTimer = 0; // spawn immediately on first tick
    this.downsThisWave = 0;
    this.smartBombUsed = false;
    this.totalFixes = 0;
    this.totalDowns = 0;
  }

  pause(): void {
    if (this.state.status === 'running') this.state.status = 'paused';
  }

  resume(): void {
    if (this.state.status === 'paused') this.state.status = 'running';
  }

  get isSmartBombAvailable(): boolean {
    return !this.smartBombUsed && this.state.status === 'running';
  }

  /* ---- Per-frame simulation ---- */

  update(dtRaw: number): void {
    if (this.state.status !== 'running') return;
    const dt = Math.min(Math.max(dtRaw, 0), 0.1); // clamp to survive tab stalls
    const s = this.state;

    s.elapsed += dt;
    this.waveElapsed += dt;
    this.spawnTimer -= dt;

    if (this.waveElapsed >= TUNING.waveDuration) this.advanceWave();

    // Activate new failing modules up to the wave's target.
    const activeCount = s.cells.reduce((n, c) => n + (c.active ? 1 : 0), 0);
    if (this.spawnTimer <= 0 && activeCount < activeTargetForWave(s.wave)) {
      this.activateRandom();
      this.spawnTimer = this.spawnInterval();
    }

    const rate = this.degradeRate();
    for (const c of s.cells) {
      if (c.status === 'down') {
        c.downTimer -= dt;
        if (c.downTimer <= 0) { c.status = 'idle'; c.stress = 0; }
        continue;
      }
      if (!c.active) continue;

      c.stress += rate * dt;
      if (c.stress >= TUNING.downThreshold) {
        this.moduleDown(c);
      } else if (c.stress >= TUNING.criticalThreshold) {
        c.status = 'critical';
      } else if (c.stress >= TUNING.warningThreshold) {
        c.status = 'warning';
      } else {
        c.status = 'charging';
      }
    }
  }

  /* ---- Player input ---- */

  /** Attempt to fix the module at `index`. */
  fix(index: number): void {
    const s = this.state;
    if (s.status !== 'running') return;
    const c = s.cells[index];
    if (!c) return;

    if (c.status === 'down') return; // already offline — neutral no-op
    if (c.status === 'idle') { this.misclick(index); return; }

    // Valid fix: charging / warning / critical
    const critical = c.status === 'critical';
    s.combo += 1;
    s.maxCombo = Math.max(s.maxCombo, s.combo);

    const base =
      c.status === 'critical' ? TUNING.scoreCritical :
      c.status === 'warning' ? TUNING.scoreWarning :
      TUNING.scoreCharging;
    const points = base * s.combo;
    s.score += points;

    const heal =
      c.status === 'critical' ? TUNING.healCritical :
      c.status === 'warning' ? TUNING.healWarning :
      TUNING.healCharging;
    s.uptime = Math.min(100, s.uptime + heal);

    c.active = false;
    c.stress = 0;
    c.status = 'idle';
    this.totalFixes += 1;

    this.hooks.onFix?.({ index, points, combo: s.combo, critical, uptime: s.uptime });
  }

  /** Hidden Odoo Overdrive — clears every failing module once per run. */
  smartBomb(): boolean {
    if (!this.isSmartBombAvailable) return false;
    this.smartBombUsed = true;
    let cleared = 0;
    for (const c of this.state.cells) {
      if (c.active || c.status !== 'idle') {
        c.active = false;
        c.stress = 0;
        c.status = 'idle';
        c.downTimer = 0;
        cleared += 1;
      }
    }
    this.hooks.onSmartBomb?.({ cleared });
    return true;
  }

  /* ---- Internal transitions ---- */

  private misclick(index: number): void {
    const s = this.state;
    s.combo = 0;
    s.uptime = Math.max(0, s.uptime - TUNING.misclickPenalty);
    s.minUptime = Math.min(s.minUptime, s.uptime);
    this.hooks.onMisclick?.({ index, uptime: s.uptime });
    if (s.uptime <= 0) this.gameOver();
  }

  private moduleDown(c: Cell): void {
    const s = this.state;
    c.active = false;
    c.status = 'down';
    c.stress = TUNING.downThreshold;
    c.downTimer = TUNING.downCooldown;
    s.combo = 0;
    this.downsThisWave += 1;
    this.totalDowns += 1;
    s.uptime = Math.max(0, s.uptime - TUNING.downPenalty);
    s.minUptime = Math.min(s.minUptime, s.uptime);
    this.hooks.onDown?.({ index: s.cells.indexOf(c), uptime: s.uptime });
    if (s.uptime <= 0) this.gameOver();
  }

  private advanceWave(): void {
    const s = this.state;
    const completed = s.wave;
    const perfect = this.downsThisWave === 0;
    const bonus = TUNING.waveClearBonus * completed;
    s.score += bonus;
    s.wave += 1;
    this.waveElapsed = 0;
    this.downsThisWave = 0;
    this.hooks.onWaveUp?.({ wave: s.wave, perfect, bonus });
  }

  private activateRandom(): void {
    const idle = this.state.cells.filter((c) => c.status === 'idle' && !c.active);
    if (idle.length === 0) return;
    const c = idle[Math.floor(Math.random() * idle.length)];
    c.active = true;
    c.status = 'charging';
    c.stress = 0;
  }

  private gameOver(): void {
    const s = this.state;
    s.status = 'over';
    const isBest = s.score > s.best;
    if (isBest) s.best = s.score;
    const summary: GameSummary = {
      score: s.score,
      best: s.best,
      isBest,
      wave: s.wave,
      durationSec: Math.round(s.elapsed),
      fixes: this.totalFixes,
      downs: this.totalDowns,
      maxCombo: s.maxCombo,
      rank: getRank(s.score),
    };
    this.hooks.onGameOver?.(summary);
  }

  private degradeRate(): number {
    return TUNING.baseDegradeRate * Math.pow(TUNING.degradeWaveMultiplier, this.state.wave - 1);
  }

  private spawnInterval(): number {
    return Math.max(
      TUNING.minSpawnInterval,
      TUNING.baseSpawnInterval * Math.pow(TUNING.spawnWaveMultiplier, this.state.wave - 1),
    );
  }
}
