// @ts-check
import { defineConfig, fontProviders } from 'astro/config';
import react from '@astrojs/react';
import sitemap from '@astrojs/sitemap';

// Pages that are noindexed, so they stay out of the sitemap too.
const NOINDEX_PATHS = ['/404/', '/blog/', '/privacy/', '/terms/'];

// https://astro.build/config
export default defineConfig({
  site: 'https://arunalexgeorge.online',
  // GitHub Pages serves every page as a directory. Linking to /about instead
  // of /about/ costs a redirect, and behind Cloudflare that redirect drops to
  // plain http://, so every internal link and canonical ends in a slash.
  trailingSlash: 'always',
  integrations: [
    react(),
    sitemap({
      filter: (page) => !NOINDEX_PATHS.includes(new URL(page).pathname),
    }),
  ],
  // Self-hosted at build time, so pages no longer wait on fonts.googleapis.com.
  fonts: [
    {
      provider: fontProviders.google(),
      name: 'Inter',
      cssVariable: '--font-inter',
      weights: ['400 700'],
      styles: ['normal'],
      subsets: ['latin'],
      fallbacks: ['system-ui', 'sans-serif'],
    },
    {
      provider: fontProviders.google(),
      name: 'Space Grotesk',
      cssVariable: '--font-space-grotesk',
      weights: ['400 700'],
      styles: ['normal'],
      subsets: ['latin'],
      fallbacks: ['system-ui', 'sans-serif'],
    },
  ],
  output: 'static',
  build: {
    assets: '_assets',
  },
  vite: {
    css: {
      devSourcemap: true,
    },
  },
});
