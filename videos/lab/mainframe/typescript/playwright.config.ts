import { defineConfig } from '../../distributed/node_modules/@playwright/test';
import path from 'node:path';
const evidence = process.env.EVIDENCE_DIR || path.resolve(__dirname, '../evidence');

export default defineConfig({
  testDir: '.',
  testMatch: 'hybrid.spec.ts',
  workers: 1,
  timeout: 30000,
  retries: 0,
  reporter: [['line'], ['junit', { outputFile: path.join(evidence, 'hybrid-typescript-tests.xml') }]],
  outputDir: path.join(evidence, 'ts-test-results'),
  use: {
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:3000',
    channel: process.env.PW_BROWSER_CHANNEL || undefined,
    trace: 'on',
  },
});
