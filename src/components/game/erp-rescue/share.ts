/* ============================================================
   ERP RESCUE — Sharing (text, social links, Web Share, image card)
   ============================================================ */

import { track } from './analytics';

const PLAY_URL = 'https://arunalexgeorge.online/play';

export interface ShareData {
  score: number;
  wave: number;
  rank: string;
}

export function buildShareText({ score, wave, rank }: ShareData): string {
  return `I kept the ERP systems online and scored ${score.toLocaleString()} on "ERP Rescue" — surviving to Wave ${wave} as a ${rank}. 🛠️ Think you can run operations better?`;
}

/** Native share when available (may include the generated image). */
export async function shareResult(data: ShareData, file?: File | null): Promise<boolean> {
  const text = buildShareText(data);
  const nav = navigator as Navigator & { canShare?: (d: ShareData) => boolean };
  if (typeof navigator !== 'undefined' && typeof navigator.share === 'function') {
    try {
      const payload: ShareData & { files?: File[] } = { title: 'ERP Rescue', text, url: PLAY_URL } as never;
      if (file && nav.canShare?.({ files: [file] } as never)) payload.files = [file];
      await navigator.share(payload as never);
      track('game_share', { method: 'native', score: data.score });
      return true;
    } catch { return false; }
  }
  return false;
}

export const socialLinks = {
  twitter(data: ShareData): string {
    const text = encodeURIComponent(buildShareText(data));
    return `https://twitter.com/intent/tweet?text=${text}&url=${encodeURIComponent(PLAY_URL)}`;
  },
  linkedin(): string {
    return `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(PLAY_URL)}`;
  },
  whatsapp(data: ShareData): string {
    return `https://wa.me/?text=${encodeURIComponent(`${buildShareText(data)} ${PLAY_URL}`)}`;
  },
};

export async function copyResult(data: ShareData): Promise<boolean> {
  const text = `${buildShareText(data)} ${PLAY_URL}`;
  try {
    await navigator.clipboard.writeText(text);
    track('game_share', { method: 'copy', score: data.score });
    return true;
  } catch { return false; }
}

/* ---- Canvas share card (1200×630 OG-sized image) ---- */

const CARD_W = 1200;
const CARD_H = 630;

export async function drawShareCard(canvas: HTMLCanvasElement, data: ShareData): Promise<void> {
  canvas.width = CARD_W;
  canvas.height = CARD_H;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  try { await (document as Document & { fonts?: FontFaceSet }).fonts?.ready; } catch { /* ignore */ }

  // Background
  ctx.fillStyle = '#09090B';
  ctx.fillRect(0, 0, CARD_W, CARD_H);

  // Emerald glow
  const glow = ctx.createRadialGradient(CARD_W - 200, 140, 40, CARD_W - 200, 140, 620);
  glow.addColorStop(0, 'rgba(16,185,129,0.22)');
  glow.addColorStop(1, 'rgba(16,185,129,0)');
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, CARD_W, CARD_H);

  // Border frame
  ctx.strokeStyle = 'rgba(46,46,50,1)';
  ctx.lineWidth = 2;
  ctx.strokeRect(24, 24, CARD_W - 48, CARD_H - 48);

  const pad = 80;

  // Eyebrow
  ctx.fillStyle = '#10B981';
  ctx.font = "600 26px 'Space Grotesk', system-ui, sans-serif";
  ctx.textBaseline = 'alphabetic';
  ctx.fillText('E R P   R E S C U E', pad, 130);

  // Score
  ctx.fillStyle = '#FAFAFA';
  ctx.font = "700 150px 'Space Grotesk', system-ui, sans-serif";
  ctx.fillText(data.score.toLocaleString(), pad, 300);

  ctx.fillStyle = '#A1A1AA';
  ctx.font = "500 34px 'Inter', system-ui, sans-serif";
  ctx.fillText('final score', pad, 350);

  // Rank + wave chips
  ctx.font = "600 30px 'Space Grotesk', system-ui, sans-serif";
  chip(ctx, pad, 410, data.rank, '#10B981');
  const rankW = ctx.measureText(data.rank).width + 56;
  chip(ctx, pad + rankW + 20, 410, `Wave ${data.wave}`, '#A1A1AA');

  // Footer
  ctx.fillStyle = '#71717A';
  ctx.font = "500 30px 'Inter', system-ui, sans-serif";
  ctx.fillText('Can you keep operations online longer?', pad, 540);
  ctx.fillStyle = '#FAFAFA';
  ctx.font = "600 30px 'Space Grotesk', system-ui, sans-serif";
  ctx.fillText('arunalexgeorge.online/play', pad, 580);
}

function chip(ctx: CanvasRenderingContext2D, x: number, y: number, label: string, color: string): void {
  const w = ctx.measureText(label).width + 56;
  const h = 56;
  ctx.strokeStyle = color;
  ctx.fillStyle = 'rgba(16,185,129,0.08)';
  ctx.lineWidth = 1.5;
  roundRect(ctx, x, y - h + 12, w, h, 28);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = color;
  ctx.fillText(label, x + 28, y);
}

function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number): void {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

export async function cardToFile(canvas: HTMLCanvasElement): Promise<File | null> {
  return new Promise((resolve) => {
    try {
      canvas.toBlob((blob) => {
        resolve(blob ? new File([blob], 'erp-rescue-score.png', { type: 'image/png' }) : null);
      }, 'image/png');
    } catch { resolve(null); }
  });
}
