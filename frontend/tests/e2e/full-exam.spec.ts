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
  // A finished section shows its score block. Whether that is a band or a raw
  // score depends on the paper's length, which the backend tests pin down; the
  // UI assertion must not depend on which paper happens to be newest.
  await expect(cards.nth(0).locator('.stage-band')).toBeVisible();

  // Reading.
  await cards.nth(1).getByRole('button').click();
  await page.waitForURL(/dashboard\/tests\/\d+\?session=/, { timeout: 20000 });
  page.once('dialog', (d) => void d.accept());
  await page.getByRole('button', { name: /Imtihonni yakunlash/ }).click();
  await page.waitForURL(/dashboard\/full\//, { timeout: 20000 });
  await expect(cards.nth(2).getByRole('button')).toBeVisible();

  expect(errors, errors.join('\n')).toEqual([]);
});

/**
 * The result form is a rendering of one payload, so it is tested against one.
 *
 * Driving four sections through the browser to reach this state costs two
 * minutes of CI and proves things the backend tests already prove; the
 * server's own tests cover how the payload is built. What only the browser
 * can show is that the form renders from it and that printing yields the
 * report alone.
 */
const FINISHED = {
  id: '11111111-2222-3333-4444-555555555555',
  state: 'completed',
  started_at: '2026-03-04T09:00:00Z',
  completed_at: '2026-03-04T12:00:00Z',
  current: 4,
  overall_band: 6.5,
  awaiting_assessment: [],
  sections_without_band: [],
  estimated: true,
  note: 'AI va jadval asosidagi taxminiy natija. Rasmiy IELTS bandi emas.',
  stages: [
    { section: 'Listening', exam_id: 1, title: 'L', duration_seconds: 2400, question_count: 40,
      order: 0, attempt_id: 'a1', state: 'graded', band: 7.0, band_source: 'table', correct: 30, total: 40 },
    { section: 'Reading', exam_id: 2, title: 'R', duration_seconds: 3600, question_count: 40,
      order: 1, attempt_id: 'a2', state: 'graded', band: 7.0, band_source: 'table', correct: 30, total: 40 },
    { section: 'Writing', exam_id: 3, title: 'W', duration_seconds: 3600, question_count: 2,
      order: 2, attempt_id: 'a3', state: 'graded', band: 6.0, band_source: 'ai_estimate', correct: null, total: null },
    { section: 'Speaking', exam_id: 4, title: 'S', duration_seconds: 900, question_count: 8,
      order: 3, attempt_id: 'a4', state: 'graded', band: 6.0, band_source: 'ai_estimate', correct: null, total: null },
  ],
};

async function openReport(page: import('@playwright/test').Page, sitting: unknown) {
  await page.route(`**/api/sessions/${FINISHED.id}/`, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(sitting) }));
  await page.goto(`/dashboard/full/${FINISHED.id}`);
  await page.waitForSelector('.result-form');
}

test('a finished sitting shows a result form', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto('/register');
  await page.getByLabel(/ismingiz|name/i).fill('Report Tester');
  await page.getByLabel(/email/i).fill(`report-${Date.now()}@example.com`);
  await page.getByLabel(/parol|password/i).fill(PASSWORD);
  await page.getByRole('button', { name: /hisob yaratish|register/i }).click();
  await page.waitForURL(/dashboard/, { timeout: 20000 });

  await openReport(page, FINISHED);
  const form = page.locator('.result-form');

  await expect(form.locator('.result-form-band > span')).toHaveText(
    ['LISTENING', 'READING', 'WRITING', 'SPEAKING', 'Umumiy band'],
    { useInnerText: true, ignoreCase: true });
  await expect(form.locator('.result-form-band > strong')).toHaveText(
    ['7.0', '7.0', '6.0', '6.0', '6.5']);

  // The date is formatted here, not by whatever locale data the browser has.
  await expect(form.getByText('04.03.2026')).toBeVisible();
  await expect(form.getByText('Report Tester')).toBeVisible();
  await expect(form.getByText(/Rasmiy IELTS Test Report Form emas/)).toBeVisible();

  expect(errors, errors.join('\n')).toEqual([]);
});

test('an unassessed section withholds the overall band and says why', async ({ page }) => {
  await page.goto('/register');
  await page.getByLabel(/ismingiz|name/i).fill('Pending Tester');
  await page.getByLabel(/email/i).fill(`pending-${Date.now()}@example.com`);
  await page.getByLabel(/parol|password/i).fill(PASSWORD);
  await page.getByRole('button', { name: /hisob yaratish|register/i }).click();
  await page.waitForURL(/dashboard/, { timeout: 20000 });

  await openReport(page, {
    ...FINISHED,
    overall_band: null,
    awaiting_assessment: ['Speaking'],
    stages: FINISHED.stages.map((s) => (s.section === 'Speaking' ? { ...s, band: null, state: 'awaiting_assessment' } : s)),
  });
  const form = page.locator('.result-form');
  await expect(form.locator('.result-form-overall strong')).toHaveText('—');
  await expect(form.getByText(/baholanmoqda: Speaking/)).toBeVisible();
});

test('a paper with no band table shows its raw score instead', async ({ page }) => {
  await page.goto('/register');
  await page.getByLabel(/ismingiz|name/i).fill('Raw Tester');
  await page.getByLabel(/email/i).fill(`raw-${Date.now()}@example.com`);
  await page.getByLabel(/parol|password/i).fill(PASSWORD);
  await page.getByRole('button', { name: /hisob yaratish|register/i }).click();
  await page.waitForURL(/dashboard/, { timeout: 20000 });

  await openReport(page, {
    ...FINISHED,
    overall_band: null,
    sections_without_band: ['Listening'],
    stages: FINISHED.stages.map((s) => (s.section === 'Listening'
      ? { ...s, band: null, band_source: 'none', correct: 5, total: 6, question_count: 6 } : s)),
  });
  const form = page.locator('.result-form');
  await expect(form.locator('.result-form-band > strong').first()).toHaveText('5/6');
  await expect(form.locator('.result-form-overall strong')).toHaveText('—');
  await expect(form.getByText(/band jadvali yo‘q/)).toBeVisible();
});

test('printing a sitting yields the report alone', async ({ page }) => {
  await page.goto('/register');
  await page.getByLabel(/ismingiz|name/i).fill('Print Tester');
  await page.getByLabel(/email/i).fill(`print-${Date.now()}@example.com`);
  await page.getByLabel(/parol|password/i).fill(PASSWORD);
  await page.getByRole('button', { name: /hisob yaratish|register/i }).click();
  await page.waitForURL(/dashboard/, { timeout: 20000 });

  await openReport(page, FINISHED);
  await page.emulateMedia({ media: 'print' });
  for (const selector of ['.site-header', '.full-exam-stages', '.result-form .no-print',
                          '.full-exam-layout > .page-heading']) {
    expect(await page.locator(selector).first().evaluate((el) => getComputedStyle(el).display),
      `${selector} must not print`).toBe('none');
  }
  await expect(page.locator('.result-form')).toBeVisible();
  await expect(page.locator('.result-form-overall strong')).toHaveText('6.5');
});
