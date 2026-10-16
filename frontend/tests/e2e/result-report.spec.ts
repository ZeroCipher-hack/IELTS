import { test, expect } from '@playwright/test';

/**
 * The AI report and the raw-score report are rendered from one attempt each,
 * so they are tested against one attempt each.
 *
 * These blocks lost every CSS rule when the design system was rewritten --
 * the class names survived in the components and nothing matched them, so a
 * report read "6.5AI band" and "task response4.5". A rule that exists only
 * inside a media query counts as missing too: .report-summary had one for
 * narrow screens and none for wide ones, and the panels touched on a desktop.
 */
const PASSWORD = 'Strong-Test-123!';
const ID = '99999999-8888-7777-6666-555555555555';

const ASSESSED = {
  id: ID, title: 'Academic Writing', section: 'Writing', state: 'graded',
  deadline: '2026-03-04T10:00:00Z', server_time: '2026-03-04T11:00:00Z',
  started_at: '2026-03-04T09:00:00Z', answers: {}, review_positions: [],
  result: {
    correct: 0, total: 0, rows: [], skills: {}, weekly_plan: [], band: 6.5,
    assessment: {
      kind: 'ai_writing', estimated: true, band: 6.5, model: 'gemini-2.5-flash',
      note: 'AI practice estimate; not an official IELTS score.',
      strengths: 'Clear overall structure.',
      tasks: [{
        position: 1, band: 5.5,
        criteria: { task_response: 4.5, coherence_cohesion: 6.0, lexical_resource: 5.5, grammar: 6.0 },
        evidence: 'The highest and lowest figures can be identified.',
        feedback: 'The overview names the extremes but does not report them.',
        improvement: 'State the highest and lowest months with their values.',
      }],
    },
  },
};

const RAW = {
  ...ASSESSED, section: 'Reading', title: 'Academic Reading',
  result: {
    correct: 15, total: 40, band: null, weekly_plan: [],
    skills: { 'True / False / Not Given': { correct: 6, total: 17 },
              'Short answer': { correct: 4, total: 4 } },
    rows: [{ position: 1, prompt: 'Q1', answer: 'TRUE', correct: true,
             accepted_answers: ['TRUE'], evidence: 'E', explanation: 'X',
             skill_tag: 'True / False / Not Given' }],
    note: 'Raw score only.',
  },
};

/** One account for the file: the server allows ten registrations per IP in
    five minutes, and a suite that spends them on repetition starts answering
    429 the moment CI retries a test. */
let signedIn: Awaited<ReturnType<import('@playwright/test').BrowserContext['cookies']>> = [];

test.beforeAll(async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('/register');
  await page.getByLabel(/ismingiz|name/i).fill('Report Reader');
  await page.getByLabel(/email/i).fill(`reader-${Date.now()}@example.com`);
  await page.getByLabel(/parol|password/i).fill(PASSWORD);
  await page.getByRole('button', { name: /hisob yaratish|register/i }).click();
  await page.waitForURL(/dashboard/, { timeout: 20000 });
  signedIn = await context.cookies();
  await context.close();
});

test.beforeEach(async ({ page }) => {
  await page.context().addCookies(signedIn);
});

async function open(page: import('@playwright/test').Page, attempt: unknown) {
  await page.route(`**/api/attempts/${ID}/`, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(attempt) }));
  await page.goto(`/dashboard/results/${ID}`);
}

test('an AI report lays out its band and criteria', async ({ page }) => {
  await open(page, ASSESSED);
  await page.waitForSelector('.ai-score-card');

  // The band and its label are separate blocks, not "6.5AI band".
  const band = page.locator('.ai-score-value');
  await expect(band.locator('strong')).toHaveText('6.5');
  expect(await band.evaluate((el) => getComputedStyle(el).display)).toBe('grid');

  // Four criteria, each a labelled cell rather than a run-on line.
  const criteria = page.locator('.criteria-list .criterion');
  await expect(criteria).toHaveCount(4);
  expect(await page.locator('.criteria-list').evaluate((el) =>
    getComputedStyle(el).gridTemplateColumns.split(' ').length)).toBe(4);
  const first = await criteria.first().boundingBox();
  const second = await criteria.nth(1).boundingBox();
  expect(second!.x).toBeGreaterThan(first!.x + first!.width);

  await expect(page.locator('.recommendation')).toBeVisible();
});

test('a raw-score report puts its two summary panels side by side', async ({ page }) => {
  await open(page, RAW);
  await page.waitForSelector('.report-summary');
  const panels = page.locator('.report-summary > .panel');
  await expect(panels).toHaveCount(2);
  const left = await panels.first().boundingBox();
  const right = await panels.nth(1).boundingBox();
  expect(right!.x, 'the panels must not stack and touch on a wide screen')
    .toBeGreaterThan(left!.x + left!.width);
  await expect(page.locator('.result-tags .panel')).toHaveCount(2);
});

test('Speaking is reached through Imtihonlar, not its own nav item', async ({ page }) => {
  await page.goto('/dashboard');
  const nav = page.getByRole('navigation');
  await expect(nav.getByRole('link', { name: 'Speaking', exact: true })).toHaveCount(0);
  await expect(nav.getByRole('link', { name: /Imtihonlar|Tests/ })).toBeVisible();
});
