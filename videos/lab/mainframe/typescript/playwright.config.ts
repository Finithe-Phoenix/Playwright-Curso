import { defineConfig } from '../../distributed/node_modules/@playwright/test';
import path from 'node:path';

export default defineConfig({
  testDir: '.',
  testMatch: 'hybrid.spec.ts',
  workers: 1,
  timeout: 30000,
  retries: 0,
  reporter: [['line'], ['junit', { outputFile: path.resolve(__dirname, '../evidence/hybrid-typescript-tests.xml') }]],
  outputDir: path.resolve(__dirname, '../evidence/ts-test-results'),
  use: {
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:3000',
    channel: process.env.PW_BROWSER_CHANNEL || undefined,
    trace: 'on',
  },
});
