import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: '.', testMatch: 'record.spec.ts', workers: 1, retries: 0,
  timeout: 90000, outputDir: '../../../motion/local-results/capture',
  reporter: [['list'], ['json', { outputFile: '../../../motion/local-results/capture-results.json' }]],
  use: { baseURL: process.env.BASE_URL || 'http://127.0.0.1:3600',
    channel: 'msedge', viewport: { width: 1280, height: 900 },
    video: { mode: 'on', size: { width: 1280, height: 900 } }, trace: 'on', headless: true },
});
