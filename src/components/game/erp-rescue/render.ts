/* ============================================================
   ERP RESCUE — View controller
   Binds the server-rendered DOM to the engine: render loop,
   input (pointer / keyboard / number keys), HUD, effects,
   achievements, sound, sharing & analytics.
   ============================================================ */

import { RescueEngine } from './engine';
import { type ModuleStatus, type GameSummary } from './types';
import { storage } from './storage';
import { track } from './analytics';
import { sfx, initAudio, setMuted } from './audio';
import { AchievementTracker, type Achievement } from './achievements';
import {
  buildShareText, shareResult, socialLinks, copyResult,
  drawShareCard, cardToFile, type ShareData,
} from './share';

export function mountErpRescue(root: HTMLElement): void {
  const $ = <T extends HTMLElement = HTMLElement>(sel: string) => root.querySelector<T>(sel);
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- Elements ----
  const screens = {
    intro: $('[data-screen="intro"]')!,
    game: $('[data-screen="game"]')!,
    over: $('[data-screen="over"]')!,
  };
  const cells = Array.from(root.querySelectorAll<HTMLButtonElement>('.erp-cell'));
  const el = {
    start: $<HTMLButtonElement>('#erp-start')!,
    again: $<HTMLButtonElement>('#erp-again')!,
    mute: $<HTMLButtonElement>('#erp-mute')!,
    pause: $<HTMLButtonElement>('#erp-pause')!,
    pauseOverlay: $('#erp-pause-overlay')!,
    score: $('#erp-score')!,
    wave: $('#erp-wave')!,
    combo: $('#erp-combo')!,
    uptimeFill: $('#erp-uptime-fill')!,
    uptimeVal: $('#erp-uptime-val')!,
    banner: $('#erp-banner')!,
    flash: $('#erp-flash')!,
    live: $('#erp-live')!,
    alert: $('#erp-alert')!,
    toast: $('#erp-toast')!,
    bestIntro: $('#erp-best-intro'),
    playsIntro: $('#erp-plays-intro'),
    // over screen
    finalScore: $('#erp-final-score')!,
    finalBest: $('#erp-final-best')!,
    finalRank: $('#erp-final-rank')!,
    finalWave: $('#erp-final-wave')!,
    finalFixes: $('#erp-final-fixes')!,
    finalCombo: $('#erp-final-combo')!,
    bestBadge: $('#erp-best-badge')!,
    achList: $('#erp-ach-list')!,
    card: $<HTMLCanvasElement>('#erp-card')!,
    shareNative: $<HTMLButtonElement>('#erp-share-native')!,
    shareX: $<HTMLAnchorElement>('#erp-share-x')!,
    shareIn: $<HTMLAnchorElement>('#erp-share-in')!,
    shareWa: $<HTMLAnchorElement>('#erp-share-wa')!,
    shareCopy: $<HTMLButtonElement>('#erp-share-copy')!,
    shareDownload: $<HTMLAnchorElement>('#erp-share-download')!,
  };

  // ---- State ----
  const tracker = new AchievementTracker();
  let muted = storage.getMuted();
  let earnedThisRun: Achievement[] = [];
  let raf = 0;
  let last = 0;
  let focusIndex = 0;
  const keyBuffer: string[] = [];
  const cellStatusCache: ModuleStatus[] = cells.map(() => 'idle');

  const engine = new RescueEngine({
    onFix: ({ index, points, combo, critical }) => {
      if (critical) sfx.critical(); else sfx.fix(combo);
      flashCell(index, critical);
      popPoints(index, points);
      pulse(el.combo);
      checkAch('fix', { combo, critical });
    },
    onDown: ({ index }) => {
      sfx.down();
      shakeCell(index);
      screenFlash();
      announce(`${cells[index]?.dataset.name} module went down`, true);
      pulse(el.uptimeVal);
    },
    onMisclick: ({ index }) => {
      sfx.misclick();
      nudgeCell(index);
    },
    onWaveUp: ({ wave, perfect }) => {
      sfx.wave();
      showBanner(`WAVE ${wave}`);
      announce(`Wave ${wave}${perfect ? ', zero downtime' : ''}`);
      checkAch('wave', { perfectWave: perfect });
    },
    onSmartBomb: ({ cleared }) => {
      sfx.bomb();
      screenFlash(true);
      showToastText('🟣', 'Odoo Overdrive', `Stabilised ${cleared} modules`);
      checkAch('special', { smartBomb: true });
    },
    onGameOver: (summary) => endGame(summary),
  }, storage.getBest());

  // ---- Screens ----
  function showScreen(name: keyof typeof screens): void {
    (Object.keys(screens) as (keyof typeof screens)[]).forEach((k) => {
      screens[k].hidden = k !== name;
    });
  }

  // ---- HUD + cells ----
  function syncHUD(): void {
    const s = engine.state;
    el.score.textContent = s.score.toLocaleString();
    el.wave.textContent = String(s.wave);
    el.combo.textContent = s.combo > 1 ? `×${s.combo}` : '—';
    el.combo.dataset.active = String(s.combo > 1);

    const up = Math.round(s.uptime);
    el.uptimeFill.style.width = `${Math.max(0, up)}%`;
    el.uptimeVal.textContent = `${up}%`;
    const health = up <= 25 ? 'crit' : up <= 50 ? 'warn' : 'ok';
    el.uptimeFill.dataset.health = health;
  }

  function syncCells(): void {
    const s = engine.state;
    for (let i = 0; i < cells.length; i++) {
      const c = s.cells[i];
      const cell = cells[i];
      cell.style.setProperty('--stress', String(Math.min(1, c.stress / 100)));
      if (cellStatusCache[i] !== c.status) {
        cellStatusCache[i] = c.status;
        cell.dataset.status = c.status;
        const label = statusLabel(c.status);
        cell.setAttribute('aria-label', `${c.def.name} — ${label}`);
        const statusEl = cell.querySelector('.erp-cell__status');
        if (statusEl) statusEl.textContent = label;
      }
    }
  }

  function statusLabel(status: ModuleStatus): string {
    switch (status) {
      case 'charging': return 'degrading';
      case 'warning': return 'warning';
      case 'critical': return 'critical';
      case 'down': return 'offline';
      default: return 'stable';
    }
  }

  // ---- Render loop ----
  function loop(t: number): void {
    const dt = last ? (t - last) / 1000 : 0;
    last = t;
    engine.update(dt);
    syncHUD();
    syncCells();
    if (engine.state.status === 'running') {
      raf = requestAnimationFrame(loop);
    } else {
      raf = 0;
    }
  }

  function startLoop(): void {
    if (raf) cancelAnimationFrame(raf);
    last = 0;
    raf = requestAnimationFrame(loop);
  }

  // ---- Game lifecycle ----
  function startGame(): void {
    initAudio();
    setMuted(muted);
    earnedThisRun = [];
    storage.incPlays();
    engine.start();
    cellStatusCache.fill('idle');
    cells.forEach((c) => { c.dataset.status = 'idle'; c.style.setProperty('--stress', '0'); });
    showScreen('game');
    syncHUD();
    syncCells();
    setRovingFocus(0, true);
    startLoop();
    track('game_start');
  }

  function endGame(summary: GameSummary): void {
    if (raf) { cancelAnimationFrame(raf); raf = 0; }
    if (summary.isBest) storage.setBest(summary.best);
    sfx.over();

    el.finalScore.textContent = summary.score.toLocaleString();
    el.finalBest.textContent = summary.best.toLocaleString();
    el.finalRank.textContent = summary.rank;
    el.finalWave.textContent = String(summary.wave);
    el.finalFixes.textContent = String(summary.fixes);
    el.finalCombo.textContent = `×${summary.maxCombo}`;
    el.bestBadge.hidden = !summary.isBest;

    renderEarned();
    setupShare(summary);
    showScreen('over');
    el.again.focus();

    track('game_over', {
      score: summary.score, wave: summary.wave,
      duration: summary.durationSec, fixes: summary.fixes, max_combo: summary.maxCombo,
    });
  }

  // ---- Achievements ----
  function checkAch(
    event: 'fix' | 'wave' | 'gameover' | 'special',
    extra: Partial<{ combo: number; critical: boolean; perfectWave: boolean; smartBomb: boolean }> = {},
  ): void {
    const s = engine.state;
    const newly = tracker.check({
      event,
      combo: extra.combo ?? s.combo,
      wave: s.wave,
      critical: extra.critical ?? false,
      score: s.score,
      uptime: s.uptime,
      minUptime: s.minUptime,
      perfectWave: extra.perfectWave ?? false,
      smartBomb: extra.smartBomb ?? false,
    });
    for (const a of newly) {
      earnedThisRun.push(a);
      showToastText(a.icon, a.name, a.desc);
      sfx.achievement();
      track('achievement_unlock', { id: a.id });
    }
  }

  function renderEarned(): void {
    el.achList.innerHTML = '';
    if (!earnedThisRun.length) {
      const p = document.createElement('p');
      p.className = 'erp-over__ach-empty';
      p.textContent = 'No new badges this run — go again and chase them.';
      el.achList.appendChild(p);
      return;
    }
    for (const a of earnedThisRun) {
      const chip = document.createElement('span');
      chip.className = 'erp-badge';
      chip.innerHTML = `<span class="erp-badge__icon" aria-hidden="true">${a.icon}</span> ${a.name}`;
      el.achList.appendChild(chip);
    }
  }

  // ---- Sharing ----
  function setupShare(summary: GameSummary): void {
    const data: ShareData = { score: summary.score, wave: summary.wave, rank: summary.rank };
    el.shareX.href = socialLinks.twitter(data);
    el.shareIn.href = socialLinks.linkedin();
    el.shareWa.href = socialLinks.whatsapp(data);
    [el.shareX, el.shareIn, el.shareWa].forEach((a) => {
      a.addEventListener('click', () => track('game_share', { method: a.id.replace('erp-share-', '') }), { once: true });
    });

    void drawShareCard(el.card, data).then(() => {
      try { el.shareDownload.href = el.card.toDataURL('image/png'); } catch { /* tainted */ }
    });

    el.shareNative.hidden = typeof navigator === 'undefined' || typeof navigator.share !== 'function';
    el.shareNative.onclick = async () => {
      const file = await cardToFile(el.card);
      const ok = await shareResult(data, file);
      if (!ok) await doCopy(data);
    };
    el.shareCopy.onclick = () => doCopy(data);
  }

  async function doCopy(data: ShareData): Promise<void> {
    const ok = await copyResult(data);
    flashButton(el.shareCopy, ok ? 'Copied!' : 'Copy failed');
  }

  function flashButton(btn: HTMLElement, text: string): void {
    const original = btn.dataset.label || btn.textContent || '';
    btn.dataset.label = original;
    btn.textContent = text;
    window.setTimeout(() => { btn.textContent = original; }, 1600);
  }

  // ---- Effects ----
  function flashCell(i: number, critical: boolean): void {
    const cell = cells[i];
    cell.classList.remove('erp-cell--fix', 'erp-cell--fix-crit');
    void cell.offsetWidth; // restart animation
    cell.classList.add(critical ? 'erp-cell--fix-crit' : 'erp-cell--fix');
  }
  function shakeCell(i: number): void {
    const cell = cells[i];
    cell.classList.remove('erp-cell--down');
    void cell.offsetWidth;
    cell.classList.add('erp-cell--down');
  }
  function nudgeCell(i: number): void {
    const cell = cells[i];
    cell.classList.remove('erp-cell--nudge');
    void cell.offsetWidth;
    cell.classList.add('erp-cell--nudge');
  }
  function pulse(node: HTMLElement): void {
    node.classList.remove('erp-pulse');
    void node.offsetWidth;
    node.classList.add('erp-pulse');
  }
  function screenFlash(good = false): void {
    el.flash.dataset.tone = good ? 'good' : 'bad';
    el.flash.classList.remove('erp__flash--on');
    void el.flash.offsetWidth;
    el.flash.classList.add('erp__flash--on');
  }
  let bannerTimer = 0;
  function showBanner(text: string): void {
    el.banner.textContent = text;
    el.banner.classList.add('erp-banner--on');
    window.clearTimeout(bannerTimer);
    bannerTimer = window.setTimeout(() => el.banner.classList.remove('erp-banner--on'), 1100);
  }
  function popPoints(i: number, points: number): void {
    const cell = cells[i];
    const rect = cell.getBoundingClientRect();
    const rootRect = root.getBoundingClientRect();
    const pop = document.createElement('span');
    pop.className = 'erp-pop';
    pop.textContent = `+${points}`;
    pop.style.left = `${rect.left - rootRect.left + rect.width / 2}px`;
    pop.style.top = `${rect.top - rootRect.top + 12}px`;
    root.appendChild(pop);
    const anim = pop.animate(
      prefersReduced
        ? [{ opacity: 1 }, { opacity: 0 }]
        : [{ opacity: 1, transform: 'translate(-50%, 0) scale(1)' },
           { opacity: 0, transform: 'translate(-50%, -34px) scale(1.15)' }],
      { duration: prefersReduced ? 500 : 720, easing: 'cubic-bezier(0.22,1,0.36,1)' },
    );
    anim.onfinish = () => pop.remove();
  }
  function showToastText(icon: string, title: string, desc: string): void {
    const t = document.createElement('div');
    t.className = 'erp-toast';
    t.setAttribute('role', 'status');
    t.innerHTML =
      `<span class="erp-toast__icon" aria-hidden="true">${icon}</span>` +
      `<span class="erp-toast__body"><strong>${title}</strong><span>${desc}</span></span>`;
    el.toast.appendChild(t);
    window.setTimeout(() => {
      t.animate([{ opacity: 1 }, { opacity: 0, transform: 'translateX(20px)' }],
        { duration: 300, fill: 'forwards' }).onfinish = () => t.remove();
    }, 3200);
  }

  function announce(msg: string, assertive = false): void {
    const region = assertive ? el.alert : el.live;
    region.textContent = '';
    window.setTimeout(() => { region.textContent = msg; }, 30);
  }

  // ---- Focus / keyboard ----
  function setRovingFocus(i: number, doFocus = false): void {
    focusIndex = Math.max(0, Math.min(cells.length - 1, i));
    cells.forEach((c, j) => { c.tabIndex = j === focusIndex ? 0 : -1; });
    if (doFocus) cells[focusIndex].focus();
  }

  function onGridKey(e: KeyboardEvent): void {
    const cols = 3;
    let next = focusIndex;
    switch (e.key) {
      case 'ArrowRight': next = (focusIndex + 1) % cells.length; break;
      case 'ArrowLeft': next = (focusIndex - 1 + cells.length) % cells.length; break;
      case 'ArrowDown': next = Math.min(cells.length - 1, focusIndex + cols); break;
      case 'ArrowUp': next = Math.max(0, focusIndex - cols); break;
      default: return;
    }
    e.preventDefault();
    setRovingFocus(next, true);
  }

  // ---- Pause ----
  function setPaused(paused: boolean): void {
    if (engine.state.status === 'over' || engine.state.status === 'idle') return;
    if (paused) {
      engine.pause();
      el.pauseOverlay.hidden = false;
      el.pause.setAttribute('aria-pressed', 'true');
      announce('Paused');
    } else {
      engine.resume();
      el.pauseOverlay.hidden = true;
      el.pause.setAttribute('aria-pressed', 'false');
      startLoop();
    }
  }

  function toggleMute(): void {
    muted = !muted;
    setMuted(muted);
    storage.setMuted(muted);
    el.mute.setAttribute('aria-pressed', String(muted));
    el.mute.dataset.muted = String(muted);
    if (!muted) initAudio();
  }

  // ---- Wire events ----
  el.start.addEventListener('click', startGame);
  el.again.addEventListener('click', () => { track('game_replay'); startGame(); });
  el.mute.addEventListener('click', toggleMute);
  el.pause.addEventListener('click', () => setPaused(engine.state.status !== 'paused'));
  el.pauseOverlay.addEventListener('click', () => setPaused(false));

  cells.forEach((cell, i) => {
    cell.addEventListener('click', () => { setRovingFocus(i); engine.fix(i); });
    cell.addEventListener('keydown', onGridKey);
  });

  document.addEventListener('keydown', (e) => {
    if (engine.state.status !== 'running' && engine.state.status !== 'paused') return;
    // number keys → fix
    if (e.key >= '1' && e.key <= '9') {
      const idx = Number(e.key) - 1;
      if (idx < cells.length) { setRovingFocus(idx); engine.fix(idx); }
      return;
    }
    if (e.key === 'Escape' || e.key === 'p' || e.key === 'P') {
      setPaused(engine.state.status !== 'paused');
      return;
    }
    if (e.key === 'm' || e.key === 'M') { toggleMute(); return; }
    // easter egg buffer
    if (/^[a-z]$/i.test(e.key)) {
      keyBuffer.push(e.key.toLowerCase());
      if (keyBuffer.length > 4) keyBuffer.shift();
      if (keyBuffer.join('') === 'odoo') { engine.smartBomb(); keyBuffer.length = 0; }
    }
  });

  document.addEventListener('visibilitychange', () => {
    if (document.hidden && engine.state.status === 'running') setPaused(true);
  });

  // ---- Init ----
  el.mute.setAttribute('aria-pressed', String(muted));
  el.mute.dataset.muted = String(muted);
  setMuted(muted);
  if (el.bestIntro) el.bestIntro.textContent = storage.getBest().toLocaleString();
  if (el.playsIntro) el.playsIntro.textContent = storage.getPlays().toLocaleString();
  showScreen('intro');
}
