/* ============================================================
   ERP RESCUE — Achievements / badges
   Persisted across runs. The tracker is fed a context after each
   relevant event and returns any newly-unlocked badges.
   ============================================================ */

import { storage } from './storage';

export interface Achievement {
  id: string;
  name: string;
  desc: string;
  icon: string;
}

export interface AchievementContext {
  event: 'fix' | 'wave' | 'gameover' | 'special';
  combo: number;
  wave: number;
  critical: boolean;
  score: number;
  uptime: number;
  minUptime: number;
  perfectWave: boolean;
  smartBomb: boolean;
}

type Rule = Achievement & { test: (c: AchievementContext) => boolean };

const RULES: Rule[] = [
  { id: 'first-fix', name: 'First Response', desc: 'Fix your first failing module', icon: '⚡',
    test: (c) => c.event === 'fix' },
  { id: 'combo-5', name: 'In the Zone', desc: 'Reach a ×5 combo', icon: '🔥',
    test: (c) => c.combo >= 5 },
  { id: 'combo-10', name: 'Flow State', desc: 'Reach a ×10 combo', icon: '🌊',
    test: (c) => c.combo >= 10 },
  { id: 'combo-20', name: 'Unstoppable', desc: 'Reach a ×20 combo', icon: '🚀',
    test: (c) => c.combo >= 20 },
  { id: 'wave-5', name: 'Firefighter', desc: 'Reach Wave 5', icon: '🚒',
    test: (c) => c.wave >= 5 },
  { id: 'wave-10', name: 'Incident Commander', desc: 'Reach Wave 10', icon: '🛡️',
    test: (c) => c.wave >= 10 },
  { id: 'perfect-wave', name: 'Zero Downtime', desc: 'Clear a wave with no outages', icon: '✅',
    test: (c) => c.event === 'wave' && c.perfectWave },
  { id: 'score-1000', name: 'Keeping the Lights On', desc: 'Score 1,000 in a single run', icon: '💡',
    test: (c) => c.score >= 1000 },
  { id: 'score-5000', name: 'Five Nines', desc: 'Score 5,000 in a single run', icon: '🏆',
    test: (c) => c.score >= 5000 },
  { id: 'comeback', name: 'Disaster Recovery', desc: 'Recover to 60% uptime after dropping below 15%', icon: '🧯',
    test: (c) => c.minUptime <= 15 && c.uptime >= 60 },
  { id: 'odoo-whisperer', name: 'Odoo Whisperer', desc: 'Discover the hidden Odoo Overdrive', icon: '🟣',
    test: (c) => c.event === 'special' && c.smartBomb },
];

export const ACHIEVEMENTS: Achievement[] = RULES.map(({ test, ...a }) => a);

export class AchievementTracker {
  private unlocked: Set<string>;

  constructor() {
    this.unlocked = new Set(storage.getAchievements());
  }

  isUnlocked(id: string): boolean { return this.unlocked.has(id); }
  count(): number { return this.unlocked.size; }
  total(): number { return RULES.length; }

  /** Evaluate rules against a context; persist & return newly-unlocked badges. */
  check(ctx: AchievementContext): Achievement[] {
    const newly: Achievement[] = [];
    for (const rule of RULES) {
      if (this.unlocked.has(rule.id)) continue;
      if (rule.test(ctx)) {
        this.unlocked.add(rule.id);
        const { test, ...badge } = rule;
        newly.push(badge);
      }
    }
    if (newly.length) storage.setAchievements([...this.unlocked]);
    return newly;
  }
}
