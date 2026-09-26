import { test, expect } from '@playwright/test';
import { trackConsoleErrors, uniqueEmail } from './helpers';

test.describe('Landing (marketing) sahifasi', () => {
  test('yuklanadi va asosiy elementlar ko‘rinadi', async ({ page }) => {
    const errors = trackConsoleErrors(page);
    await page.goto('/');
    await expect(page.getByRole('link', { name: /bepul urinishni boshlash|start your free attempt|начать бесплатную попытку/i }).first()).toBeVisible();
    errors.assertNone();
  });
});

test.describe('Ro‘yxatdan o‘tish va dashboard oqimi', () => {
  // Bitta yangi foydalanuvchi bilan ro'yxatdan o'tib, asosiy dashboard
  // route'larini birma-bir tekshiramiz. /dashboard/tests/[examId] va
  // /dashboard/results/[attemptId] kabi dinamik sahifalar bu yerda
  // TEKSHIRILMAYDI — ularga haqiqiy imtihon/urinish ID kerak; alohida
  // fixture/seed ma'lumot bilan qo'shimcha test yozish tavsiya etiladi.

  test('ro‘yxatdan o‘tish → dashboard, keyin barcha asosiy bo‘limlar ochiladi', async ({ page }) => {
    const errors = trackConsoleErrors(page);
    const email = uniqueEmail();

    await page.goto('/register');
    await page.getByLabel(/ismingiz|name/i).fill('E2E Test User');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/parol|password/i).fill('SuperSecret123!');
    await page.getByRole('button', { name: /hisob yaratish|register/i }).click();

    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 15_000 });
    await expect(page.getByRole('heading', { name: /xush kelibsiz|welcome/i })).toBeVisible();

    const routes: Array<[string, RegExp]> = [
      ['/dashboard/tests', /imtihonlar|tests/i],
      ['/dashboard/results', /natijalar|results/i],
      ['/dashboard/analytics', /analitika|analytics/i],
      ['/dashboard/plan', /haftalik reja|weekly plan/i],
      ['/dashboard/payments', /to‘lov|payment/i],
      ['/dashboard/speaking', /suhbatga tayyor|nova|speaking/i],
      ['/dashboard/profile', /profil|profile/i],
    ];

    for (const [path, expectedText] of routes) {
      await page.goto(path);
      await expect(page.getByText(expectedText).first()).toBeVisible({ timeout: 10_000 });
    }

    errors.assertNone();
  });

  test('login sahifasidan noto‘g‘ri parol bilan xato ko‘rsatiladi', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('no-such-user@example.com');
    await page.getByLabel(/parol|password/i).fill('wrong-password');
    await page.getByRole('button', { name: /kirish|login/i }).click();
    await expect(page.getByRole('alert')).toBeVisible({ timeout: 10_000 });
  });
});
