/* ============================================================
   ERP RESCUE — Sound (Web Audio synth, zero asset files)
   Tiny oscillator blips. Muted honours user preference and
   only ever runs after a user gesture (Start).
   ============================================================ */

let ctx: AudioContext | null = null;
let muted = false;

export function setMuted(value: boolean): void { muted = value; }

/** Lazily create/resume the audio context (call on Start). */
export function initAudio(): void {
  if (typeof window === 'undefined') return;
  try {
    if (!ctx) {
      const AC = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (AC) ctx = new AC();
    }
    if (ctx && ctx.state === 'suspended') void ctx.resume();
  } catch { /* audio unsupported */ }
}

function tone(freq: number, dur = 0.09, type: OscillatorType = 'sine', gain = 0.05, delay = 0): void {
  if (muted || !ctx) return;
  const start = ctx.currentTime + delay;
  const osc = ctx.createOscillator();
  const amp = ctx.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, start);
  amp.gain.setValueAtTime(gain, start);
  amp.gain.exponentialRampToValueAtTime(0.0001, start + dur);
  osc.connect(amp);
  amp.connect(ctx.destination);
  osc.start(start);
  osc.stop(start + dur);
}

function chord(freqs: number[], step = 0.07, dur = 0.15, gain = 0.05): void {
  freqs.forEach((f, i) => tone(f, dur, 'sine', gain, i * step));
}

export const sfx = {
  fix(combo: number): void { tone(440 + Math.min(combo, 16) * 40, 0.09, 'sine', 0.05); },
  critical(): void { tone(680, 0.11, 'triangle', 0.06); },
  wave(): void { chord([523.25, 659.25, 783.99]); },
  down(): void { tone(120, 0.24, 'sawtooth', 0.05); },
  misclick(): void { tone(170, 0.06, 'square', 0.03); },
  achievement(): void { chord([659.25, 880, 1174.66], 0.08, 0.16, 0.045); },
  bomb(): void { chord([392, 523.25, 659.25, 880], 0.05, 0.2, 0.05); },
  over(): void { chord([330, 262, 196], 0.14, 0.3, 0.05); },
};
