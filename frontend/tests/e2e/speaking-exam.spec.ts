import { test, expect } from '@playwright/test';

test.use({
  launchOptions: {
    args: ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'],
  },
  permissions: ['microphone'],
});

const EMAIL = `speak-${Date.now()}@example.com`;

test('a device with no speech voices says so and still records', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto('/register');
  await page.getByLabel(/ismingiz|name/i).fill('Speaking Tester');
  await page.getByLabel(/email/i).fill(EMAIL);
  await page.getByLabel(/parol|password/i).fill('Strong-Test-123!');
  await page.getByRole('button', { name: /hisob yaratish|register/i }).click();
  await page.waitForURL(/dashboard/, { timeout: 20000 });

  await page.goto('/dashboard/tests?section=Speaking');
  // No key is configured in this sandbox, so the honest "not assessed yet"
  // confirmation appears. Accepting it is part of the flow under test.
  page.once('dialog', (d) => void d.accept());
  await page.getByRole('button', { name: /Boshlash/ }).first().click();
  await page.waitForURL(/dashboard\/tests\/\d+/, { timeout: 20000 });

  await page.getByRole('checkbox').check();
  await page.getByRole('button', { name: /Imtihonni boshlash/ }).click();

  // Headless Chromium has no speech engine, which is exactly the user's case.
  // The exam must not stall; it must say so and open the microphone.
  await expect(page.getByText(/Yozilmoqda — javob bering/)).toBeVisible({ timeout: 25000 });
  await expect(page.getByText(/Qurilmangizda ovoz chiqmadi/)).toBeVisible();
  await expect(page.locator('.timer')).toBeVisible();
  await expect(page.getByRole('heading', { level: 2 })).toContainText(/\?/);

  // The clock really runs, so the section cannot sit forever.
  const first = await page.locator('.timer').textContent();
  await page.waitForTimeout(2500);
  expect(await page.locator('.timer').textContent()).not.toBe(first);

  expect(errors, errors.join('\n')).toEqual([]);
});
