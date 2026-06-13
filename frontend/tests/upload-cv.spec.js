import { test, expect } from '@playwright/test';
import path from 'path';

test('uploading a CV shows returned job cards', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByTestId('cv-upload-button')).toBeVisible();
  await page.setInputFiles('[data-testid="cv-upload-input"]', path.join(process.cwd(), 'tests/fixtures/sample-cv.pdf'));

  const cards = page.getByTestId('job-card');
  await expect.poll(async () => cards.count()).toBeGreaterThan(0, { timeout: 60000 });
  await expect(cards.first()).toBeVisible();
});