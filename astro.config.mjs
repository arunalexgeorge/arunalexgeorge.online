// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://arunalexgeorge.online',
  integrations: [react(), sitemap()],
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