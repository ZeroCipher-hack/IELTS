import { defineConfig, devices } from '@playwright/test';

/**
 * E2E smoke testlar. Ishga tushirishdan oldin backend (Django) ishlab
 * turishi shart — BACKEND_URL orqali ulanadi (.env.local dagi kabi).
 * Ishga tushirish: `pnpm test:e2e` (frontend/ ichida).
 */
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  // Testlarni ishga tushirishdan oldin dev serverni avtomatik ko'taradi
  // (agar allaqachon ishlab turgan bo'lsa, qayta ishga tushirmaydi).
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: true,
    timeout: 60_000,
  },
});
