import type { Page } from '@playwright/test';

/**
 * Har bir testda chaqiring: brauzer konsolida `console.error` yoki
 * ushlanmagan JS xatosi chiqsa, test yagona shu sabab bilan yiqiladi.
 * Aynan shu turdagi tekshiruv `router.replace()` render paytida
 * chaqirilgan React ogohlantirishini ham avtomatik ushlagan bo'lardi.
 */
export function trackConsoleErrors(page: Page) {
  const errors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  page.on('pageerror', (err) => errors.push(err.message));
  return {
    assertNone() {
      if (errors.length) {
        throw new Error('Brauzer konsolida xato(lar) topildi:\n' + errors.join('\n'));
      }
    },
  };
}

export function uniqueEmail() {
  return `e2e.${Date.now()}.${Math.floor(Math.random() * 10000)}@example.com`;
}
