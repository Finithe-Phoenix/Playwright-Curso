import { defineConfig } from '@playwright/test';

const evidence = process.env.ARTIFACT_DIR || 'evidence';
export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 30000,
  expect: { timeout: 5000 },
  outputDir: `${evidence}/test-results`,
  reporter: [ ['list'], ['html', { outputFolder: `${evidence}/html-report`, open: 'never' }],
    ['json', { outputFile: `${evidence}/results.json` }], ['junit', { outputFile: `${evidence}/results.xml` }] ],
  use: {
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:3000',
    viewport: { width: 1440, height: 960 },
    trace: 'on', // Keep all traces for this recorded lesson, including successful examples.
    screenshot: 'on',
    video: 'on',
    headless: true,
  },
  projects: [{ name: 'chromium', use: { browserName: 'chromium', channel: process.env.PW_CHANNEL || 'msedge' } }],
});
