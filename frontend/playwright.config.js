import { defineConfig } from '@playwright/test';
import { existsSync } from 'node:fs';

const windowsPython = '../.venv/Scripts/python.exe';
const unixPython = '../.venv/bin/python';
const python = existsSync(windowsPython)
  ? windowsPython
  : existsSync(unixPython)
    ? unixPython
    : 'python';

export default defineConfig({
  testDir: './tests',
  testMatch: '*.spec.js',
  fullyParallel: false,
  workers: 1,
  timeout: 30000,
  use: {
    baseURL: 'http://127.0.0.1:5175',
    browserName: 'chromium',
    ...(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {}),
    viewport: { width: 1440, height: 1100 },
    trace: 'retain-on-failure',
  },
  webServer: [
    {
      command: `"${python}" tests/serve_backend.py`,
      url: 'http://127.0.0.1:8751/health',
      timeout: 60000,
      reuseExistingServer: false,
      env: { PYTHONPATH: '../backend' },
    },
    {
      command: 'npm run dev -- --port 5175',
      url: 'http://127.0.0.1:5175',
      timeout: 30000,
      reuseExistingServer: false,
      env: { BACKEND_URL: 'http://127.0.0.1:8751' },
    },
  ],
});
