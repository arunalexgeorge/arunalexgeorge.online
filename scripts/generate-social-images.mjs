// Generates the default social-share image and the PNG favicons that
// BaseLayout links to. Run with `npm run generate:social` after changing the
// avatar, the favicon or the wording below; the outputs are committed.
import sharp from 'sharp';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = (path) => fileURLToPath(new URL(`../${path}`, import.meta.url));

const BG = '#09090B';
const ACCENT = '#10B981';
const TEXT = '#FAFAFA';
const MUTED = '#A1A1AA';
const FONT = "'Space Grotesk', 'Helvetica Neue', Helvetica, Arial, sans-serif";

// --- Open Graph image, 1200 x 630 -------------------------------------------
const avatarSize = 360;
const avatar = await sharp(root('src/assets/images/hero-avatar.png'))
  .resize(avatarSize, avatarSize)
  .toBuffer();

const card = `
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <radialGradient id="glow" cx="78%" cy="45%" r="45%">
      <stop offset="0%" stop-color="${ACCENT}" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="${ACCENT}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="630" fill="${BG}"/>
  <rect width="1200" height="630" fill="url(#glow)"/>
  <rect x="0" y="0" width="1200" height="6" fill="${ACCENT}"/>
  <circle cx="990" cy="315" r="${avatarSize / 2 + 14}" fill="none" stroke="${ACCENT}" stroke-opacity="0.45" stroke-width="2"/>
  <text x="80" y="150" font-family="${FONT}" font-size="26" font-weight="600" fill="${ACCENT}" letter-spacing="3">ODOO · ERP · AUTOMATION</text>
  <text x="80" y="250" font-family="${FONT}" font-size="76" font-weight="700" fill="${TEXT}">Arun Alex George</text>
  <text x="80" y="320" font-family="${FONT}" font-size="34" font-weight="500" fill="${TEXT}">Senior Odoo Developer &amp; ERP Consultant</text>
  <text x="80" y="390" font-family="${FONT}" font-size="28" fill="${MUTED}">Custom modules · Implementation · Migration</text>
  <text x="80" y="432" font-family="${FONT}" font-size="28" fill="${MUTED}">Odoo apps &amp; themes on the Odoo App Store</text>
  <text x="80" y="545" font-family="${FONT}" font-size="28" font-weight="600" fill="${TEXT}">arunalexgeorge<tspan fill="${ACCENT}">.</tspan>online</text>
</svg>`;

await sharp(Buffer.from(card))
  .composite([{ input: avatar, left: 990 - avatarSize / 2, top: 315 - avatarSize / 2 }])
  .png({ compressionLevel: 9, palette: true, quality: 90 })
  .toFile(root('public/og-image.png'));

// --- Favicons from favicon.svg ------------------------------------------------
const favicon = await readFile(root('public/favicon.svg'));
await sharp(favicon, { density: 300 }).resize(32, 32).png().toFile(root('public/favicon-32x32.png'));
// Apple touch icons are shown without transparency, so the square is filled.
await sharp(favicon, { density: 1200 })
  .resize(180, 180)
  .flatten({ background: BG })
  .png()
  .toFile(root('public/apple-touch-icon.png'));

console.log('Wrote public/og-image.png, public/favicon-32x32.png, public/apple-touch-icon.png');
