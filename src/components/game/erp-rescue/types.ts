/* ============================================================
   ERP RESCUE — Types, module catalogue & game tuning
   Single source of truth shared by the engine (logic) and the
   Astro component (server-rendered grid). No DOM references here.
   ============================================================ */

/** Runtime state of a single business module on the grid. */
export type ModuleStatus =
  | 'idle'      // stable, not degrading — not fixable
  | 'charging'  // degrading, below the warning line — fixable (low value)
  | 'warning'   // degrading past the warning line — fixable (mid value)
  | 'critical'  // about to fail — fixable (high value + reward)
  | 'down';     // just failed, in recovery cooldown — not fixable

export type GameStatus = 'idle' | 'running' | 'paused' | 'over';

/** Static definition of a business module (rendered server-side). */
export interface ModuleDef {
  id: string;
  name: string;   // full label, e.g. "Accounting"
  code: string;   // short mono code, e.g. "ACCT"
  /** Inline SVG paths (24x24 viewBox, stroke=currentColor). */
  icon: string;
}

/** Live per-module state tracked by the engine. */
export interface Cell {
  def: ModuleDef;
  status: ModuleStatus;
  active: boolean;   // is this module currently degrading?
  stress: number;    // 0..100
  downTimer: number; // seconds left in the down cooldown
}

export interface GameSummary {
  score: number;
  best: number;
  isBest: boolean;
  wave: number;
  durationSec: number;
  fixes: number;
  downs: number;
  maxCombo: number;
  rank: string;
}

/* ---- The 9 business modules (a 3×3 operations grid) ---- */
export const MODULES: ModuleDef[] = [
  {
    id: 'sales', name: 'Sales', code: 'SALE',
    icon: '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
  },
  {
    id: 'inventory', name: 'Inventory', code: 'INV',
    icon: '<path d="M21 8v8a2 2 0 0 1-1 1.73l-7 4a2 2 0 0 1-2 0l-7-4A2 2 0 0 1 3 16V8"/><path d="M3.3 7 12 12l8.7-5"/><path d="M12 22V12"/>',
  },
  {
    id: 'accounting', name: 'Accounting', code: 'ACCT',
    icon: '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
  },
  {
    id: 'manufacturing', name: 'Manufacturing', code: 'MFG',
    icon: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
  },
  {
    id: 'purchasing', name: 'Purchasing', code: 'PUR',
    icon: '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>',
  },
  {
    id: 'hr', name: 'Human Resources', code: 'HR',
    icon: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  },
  {
    id: 'crm', name: 'CRM', code: 'CRM',
    icon: '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/>',
  },
  {
    id: 'warehouse', name: 'Warehouse', code: 'WMS',
    icon: '<path d="M3 21V8l9-5 9 5v13"/><path d="M3 21h18"/><rect x="8" y="13" width="8" height="8"/>',
  },
  {
    id: 'api', name: 'API Gateway', code: 'API',
    icon: '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>',
  },
];

/* ---- Game tuning (adjust freely — all balance lives here) ---- */
export const TUNING = {
  gridSize: MODULES.length,

  // Stress thresholds (0..100)
  warningThreshold: 40,
  criticalThreshold: 75,
  downThreshold: 100,

  // Degradation
  baseDegradeRate: 16,        // stress/sec for an active module at wave 1
  degradeWaveMultiplier: 1.13,

  // Spawning of new failing modules
  baseSpawnInterval: 1.7,     // sec between activations while below target
  spawnWaveMultiplier: 0.92,
  minSpawnInterval: 0.55,

  // Waves
  waveDuration: 16,           // sec of survival per wave

  // Health
  startUptime: 100,
  downPenalty: 9,             // uptime lost when a module fails
  misclickPenalty: 2,         // uptime lost when tapping a stable module
  downCooldown: 1.1,          // sec a failed module stays offline

  // Healing per successful fix (rewards catching later, riskier states)
  healCharging: 0,
  healWarning: 1,
  healCritical: 2,

  // Scoring (multiplied by the current combo)
  scoreCharging: 5,
  scoreWarning: 12,
  scoreCritical: 25,
  waveClearBonus: 40,         // × completed wave number
} as const;

/** Number of modules allowed to be failing at once, by wave. */
export function activeTargetForWave(wave: number): number {
  return Math.min(TUNING.gridSize - 1, 1 + Math.floor(wave / 2));
}

/** Thematic rank derived from a score — flavour + a reason to climb. */
const RANKS: Array<{ min: number; name: string }> = [
  { min: 0, name: 'IT Intern' },
  { min: 500, name: 'Support Engineer' },
  { min: 1500, name: 'Systems Administrator' },
  { min: 3500, name: 'Site Reliability Engineer' },
  { min: 7000, name: 'Solutions Architect' },
  { min: 12000, name: 'Chief Technology Officer' },
];

export function getRank(score: number): string {
  let rank = RANKS[0].name;
  for (const r of RANKS) if (score >= r.min) rank = r.name;
  return rank;
}
