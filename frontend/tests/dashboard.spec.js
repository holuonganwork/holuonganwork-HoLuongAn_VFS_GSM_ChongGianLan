import { test, expect } from '@playwright/test';

test('unknown routes recover and the keyboard skip link keeps the active page', async ({
  page,
}) => {
  await page.goto('/#constructor');
  await expect(page.locator('h1')).toHaveText('Tổng quan hệ thống');
  await page.goto('/#drivers');
  await page.keyboard.press('Tab');
  await expect(page.locator('.skip-link')).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main')).toBeFocused();
  await expect(page.locator('h1')).toHaveText('Dữ liệu tài xế');
});

test('real API populates dashboard; the map supports details, roadmap and zoom', async ({
  page,
}, testInfo) => {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('/');
  await expect(page.locator('[data-metric="drivers"]')).toHaveText('100');
  await expect(page.locator('[data-metric="alerts"]')).toHaveText('6');
  await expect(page.locator('[data-metric="queue"]')).toHaveText('6');
  await expect(page.locator('[data-metric="cases"]')).toHaveText('6');
  await expect(page.locator('#connection')).toHaveText('API & database kết nối');
  await expect(page.locator('#outcomes')).toContainText('100%');
  await expect(page.locator('[data-node="ml"]')).toBeHidden();
  await page.locator('[data-node="assessment"]').click();
  await expect(page.getByRole('dialog')).toContainText('Điểm rủi ro không phải xác suất gian lận');
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).toBeHidden();
  const before = await page.locator('#zoom-value').textContent();
  await page.getByRole('button', { name: 'Phóng to', exact: true }).click();
  await expect(page.locator('#zoom-value')).not.toHaveText(before);
  await page.getByRole('button', { name: 'Vừa khung', exact: true }).click();
  await expect(page.locator('#zoom-value')).toHaveText(before);
  await page.getByRole('switch').check();
  await expect(page.locator('[data-node="ml"]')).toBeVisible();
  await page.locator('[data-node="ml"]').click();
  await expect(page.getByRole('dialog')).toContainText('Dự kiến mở rộng');
  await page.keyboard.press('Escape');
  await page.getByRole('switch').uncheck();
  await page.screenshot({ path: testInfo.outputPath('dashboard-desktop.png'), fullPage: true });
  expect(errors).toEqual([]);
});

test('case filters query the backend; evidence links resolve to original source records', async ({
  page,
}) => {
  await page.goto('/#cases');
  await expect(page.locator('tbody tr')).toHaveCount(6);
  await page.getByLabel('Loại dấu hiệu').selectOption('promotion_abuse');
  await page.getByRole('button', { name: 'Áp dụng', exact: true }).click();
  await expect(page.locator('tbody tr')).toHaveCount(1);
  await expect(page.locator('tbody')).toContainText('Lạm dụng khuyến mãi');
  await page.locator('[data-record]').click();
  await expect(page.getByRole('dialog')).toContainText('Bằng chứng');
  await page.locator('[data-source]').first().click();
  await expect(page.locator('.source-records details').first()).toBeVisible();
  await page.locator('.source-records summary').first().click();
  await expect(page.locator('.source-records pre').first()).toBeVisible();
  await page.keyboard.press('Escape');
  await page.getByRole('button', { name: 'Đặt lại', exact: true }).click();
  await expect(page.locator('tbody tr')).toHaveCount(6);
  await page.getByLabel('Mã ID tài xế').fill('99999');
  await page.getByRole('button', { name: 'Áp dụng', exact: true }).click();
  await expect(page.locator('#records-content')).toContainText('Không có bản ghi phù hợp');
});

test('alert details keep unknown probabilities unknown and filters show true empty results', async ({
  page,
}) => {
  await page.goto('/#alerts');
  await page.locator('[data-record]').first().click();
  await expect(page.getByRole('dialog')).toContainText('Chưa ước lượng');
  await expect(page.getByRole('dialog')).toContainText('Lý do phân luồng');
  await page.keyboard.press('Escape');
  await page.getByLabel('Phân luồng').selectOption('auto_clear');
  await page.getByRole('button', { name: 'Áp dụng', exact: true }).click();
  await expect(page.locator('#records-content')).toContainText('Không có bản ghi phù hợp');
});

test('driver pagination and details use real records', async ({ page }) => {
  await page.goto('/#drivers');
  await expect(page.locator('tbody tr')).toHaveCount(20);
  await expect(page.locator('tbody tr').first()).toContainText('D001');
  await expect(page.getByRole('button', { name: 'Trang trước' })).toBeDisabled();
  await page.getByRole('button', { name: 'Trang sau' }).click();
  await expect(page.locator('tbody tr').first()).toContainText('D021');
  await page.locator('[data-record]').first().click();
  await expect(page.getByRole('dialog')).toContainText('D021');
  await page.keyboard.press('Escape');
  await page.getByRole('button', { name: 'Trang trước' }).click();
  await expect(page.locator('tbody tr').first()).toContainText('D001');
});

test('offline mode retains architecture and recovers on refresh', async ({ page }) => {
  await page.route('**/api/**', (route) => route.abort());
  await page.goto('/');
  await expect(page.locator('.dashboard-notice')).toBeVisible();
  await expect(page.locator('[data-metric="drivers"]')).toHaveText('—');
  await expect(page.locator('#connection')).toHaveText('Chưa kết nối API');
  await page.locator('[data-node="engine"]').click();
  await expect(page.getByRole('dialog')).toContainText('RuleDetectorAdapter');
  await page.keyboard.press('Escape');
  await page.unroute('**/api/**');
  await page.getByRole('button', { name: 'Làm mới dữ liệu' }).click();
  await expect(page.locator('[data-metric="drivers"]')).toHaveText('100');
  await expect(page.locator('.dashboard-notice')).toBeHidden();
});

test('partial failure leaves independently loaded metrics visible', async ({ page }) => {
  await page.route('**/api/fraud-alerts?*', (route) => route.fulfill({ status: 503, body: '{}' }));
  await page.goto('/');
  await expect(page.locator('[data-metric="alerts"]')).toHaveText('—');
  await expect(page.locator('[data-metric="drivers"]')).toHaveText('100');
  await expect(page.locator('[data-metric="queue"]')).toHaveText('6');
  await expect(page.locator('.dashboard-notice')).toBeVisible();
});

test('mobile navigation, horizontal map scrolling and dialogs remain usable', async ({
  page,
}, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await expect(page.locator('[data-metric="drivers"]')).toHaveText('100');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
  await page.locator('[data-node="policy"]').click();
  await expect(page.getByRole('dialog')).toContainText('Decision Engine');
  await page.getByRole('button', { name: 'Đóng', exact: true }).click();
  await page.screenshot({ path: testInfo.outputPath('dashboard-mobile.png'), fullPage: true });
  await page.locator('[data-route="queue"]').click();
  await expect(page.locator('h1')).toHaveText('Hàng chờ review');
  await expect(page.locator('tbody tr')).toHaveCount(6);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
});

test('API text is rendered as text instead of executing markup', async ({ page }) => {
  await page.route('**/api/drivers?*', (route) =>
    route.fulfill({
      json: [
        {
          id: 1,
          external_driver_id: 'D001',
          name: '<img src=x onerror="window.injected=true">',
          status: 'active',
          created_at: '2026-01-05T00:00:00Z',
        },
      ],
    }),
  );
  await page.goto('/#drivers');
  await expect(page.locator('tbody')).toContainText('<img src=x');
  await expect(page.locator('tbody img')).toHaveCount(0);
  expect(await page.evaluate(() => window.injected)).toBeUndefined();
});
