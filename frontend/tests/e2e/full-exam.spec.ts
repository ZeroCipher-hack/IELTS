import { test, expect } from '@playwright/test';


const EMAIL = `full-${Date.now()}@example.com`;
const PASSWORD = 'Strong-Test-123!';

test('a full sitting runs all four sections in order', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto('/register');
  await page.getByLabel(/ismingiz|name/i).fill('Full Exam Tester');
  await page.getByLabel(/email/i).fill(EMAIL);
  await page.getByLabel(/parol|password/i).fill(PASSWORD);
  await page.getByRole('button', { name: /hisob yaratish|register/i }).click();
  await page.waitForURL(/dashboard/, { timeout: 20000 });

  await page.goto('/dashboard/tests');
  await page.getByRole('link', { name: /To‘liq imtihonni boshlash/ }).click();
  await page.waitForURL(/dashboard\/full\/[0-9a-f-]{36}/, { timeout: 20000 });

  const cards = page.locator('.full-exam-stages > li');
  await expect(cards).toHaveCount(4);
  await expect(cards.nth(0).locator('.eyebrow')).toHaveText('Listening');
  await expect(cards.nth(3).locator('.eyebrow')).toHaveText('Speaking');

  // Only the first section is startable; the rest say so.
  await expect(cards.nth(0).getByRole('button')).toBeVisible();
  await expect(cards.nth(1).getByText(/Oldingi bo‘lim tugagach/)).toBeVisible();

  const sittingUrl = page.url();

  // Listening: start it, confirm the audio element is really there, submit.
  await cards.nth(0).getByRole('button').click();
  await page.waitForURL(/dashboard\/tests\/\d+\?session=/, { timeout: 20000 });
  const audio = page.locator('audio');
  await expect(audio).toHaveCount(1);
  expect(await audio.getAttribute('src')).toContain('/media/');

  page.once('dialog', (d) => void d.accept());
  await page.getByRole('button', { name: /Imtihonni yakunlash/ }).click();
  await page.waitForURL(/dashboard\/full\//, { timeout: 20000 });
  expect(page.url()).toBe(sittingUrl);

  // The sitting advanced: Listening is done, Reading is now the live one.
  await expect(cards.nth(0).locator('.access-badge')).toContainText(/Tekshirildi/);
  await expect(cards.nth(1).getByRole('button')).toBeVisible();
  await expect(cards.nth(0).getByText(/Band jadvali yo‘q/)).toBeVisible();

  // Reading.
  await cards.nth(1).getByRole('button').click();
  await page.waitForURL(/dashboard\/tests\/\d+\?session=/, { timeout: 20000 });
  page.once('dialog', (d) => void d.accept());
  await page.getByRole('button', { name: /Imtihonni yakunlash/ }).click();
  await page.waitForURL(/dashboard\/full\//, { timeout: 20000 });
  await expect(cards.nth(2).getByRole('button')).toBeVisible();

  expect(errors, errors.join('\n')).toEqual([]);
});
