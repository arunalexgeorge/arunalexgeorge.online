/* ============================================================
   ERP RESCUE — Persistence (localStorage, SSR- & private-mode safe)
   ============================================================ */

const NS = 'erp-rescue';

function get(key: string): string | null {
  try { return localStorage.getItem(`${NS}:${key}`); } catch { return null; }
}
function set(key: string, value: string): void {
  try { localStorage.setItem(`${NS}:${key}`, value); } catch { /* ignore */ }
}

export const storage = {
  getBest(): number { return Number(get('best')) || 0; },
  setBest(n: number): void { set('best', String(n)); },

  getPlays(): number { return Number(get('plays')) || 0; },
  incPlays(): void { set('plays', String(this.getPlays() + 1)); },

  getMuted(): boolean { return get('muted') === '1'; },
  setMuted(muted: boolean): void { set('muted', muted ? '1' : '0'); },

  getAchievements(): string[] {
    try { return JSON.parse(get('ach') || '[]'); } catch { return []; }
  },
  setAchievements(ids: string[]): void { set('ach', JSON.stringify(ids)); },
};
