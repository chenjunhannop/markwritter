/**
 * Navigation E2E Tests
 *
 * Tests for basic navigation and layout functionality.
 */

import { test, expect } from './fixtures/test-fixtures';

test.describe('Navigation', () => {
  test.describe('Sidebar Navigation', () => {
    test('should display sidebar with navigation items', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('load');

      // Check sidebar is visible
      const sidebar = page.locator('nav');
      await expect(sidebar).toBeVisible();

      // Check brand name
      await expect(sidebar.getByText('Markwritter')).toBeVisible();

      // Check nav items are present (using aria-label)
      await expect(page.getByRole('button', { name: 'Chat' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Skills' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Logs' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Settings' })).toBeVisible();
    });

    test('should navigate to Skills page', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('load');

      // Click Skills button
      await page.getByRole('button', { name: 'Skills' }).click();

      // Verify URL
      await expect(page).toHaveURL(/\/skills/);
    });

    test('should navigate to Logs page', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('load');

      // Click Logs button
      await page.getByRole('button', { name: 'Logs' }).click();

      // Verify URL
      await expect(page).toHaveURL(/\/logs/);
    });

    test('should navigate to Settings page', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('load');

      // Click Settings button
      await page.getByRole('button', { name: 'Settings' }).click();

      // Verify URL
      await expect(page).toHaveURL(/\/settings/);
    });

    test('should navigate to Chat page from other pages', async ({ page }) => {
      await page.goto('/settings');
      await page.waitForLoadState('load');

      // Click Chat button
      await page.getByRole('button', { name: 'Chat' }).click();

      // Verify URL - Chat route is /chat
      await expect(page).toHaveURL(/\/chat/);
    });
  });

  test.describe('Page Headers', () => {
    test('should display Chat header on chat page', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('load');

      // Check header exists
      const header = page.locator('header');
      await expect(header).toBeVisible({ timeout: 10000 });

      // Check title
      const title = header.locator('h1');
      await expect(title).toContainText('Chat');
    });

    test('should display Skills header on skills page', async ({ skillsPage }) => {
      // Mock API to avoid errors
      await skillsPage.page.route('**/api/skills', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      });

      await skillsPage.goto();
      await skillsPage.page.waitForLoadState('load');

      // Check header exists
      const header = skillsPage.page.locator('header');
      await expect(header).toBeVisible({ timeout: 10000 });

      // Check title
      const title = header.locator('h1');
      await expect(title).toContainText('Skills');
    });

    test('should display Settings header on settings page', async ({ settingsPage }) => {
      // Mock API to avoid errors
      await settingsPage.page.route('**/api/settings', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ theme: 'system', language: 'en' }),
        });
      });

      await settingsPage.goto();
      await settingsPage.page.waitForLoadState('load');

      // Check header exists
      const header = settingsPage.page.locator('header');
      await expect(header).toBeVisible({ timeout: 10000 });

      // Check title
      const title = header.locator('h1');
      await expect(title).toContainText('Settings');
    });

    test('should display Logs header on logs page', async ({ logsPage }) => {
      await logsPage.goto();
      await logsPage.page.waitForLoadState('load');

      // Check header exists
      const header = logsPage.page.locator('header');
      await expect(header).toBeVisible({ timeout: 10000 });

      // Check title
      const title = header.locator('h1');
      await expect(title).toContainText('Logs');
    });
  });

  test.describe('Responsive Layout', () => {
    test('should display correctly on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/');
      await page.waitForLoadState('load');

      // Sidebar should be visible
      const sidebar = page.locator('nav');
      await expect(sidebar).toBeVisible({ timeout: 10000 });

      // Main content should be visible - use first() to handle multiple main elements
      const main = page.locator('main').first();
      await expect(main).toBeVisible({ timeout: 10000 });
    });

    test('should display correctly on tablet viewport', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto('/');
      await page.waitForLoadState('load');

      // Main content should be visible
      const main = page.locator('main').first();
      await expect(main).toBeVisible({ timeout: 10000 });
    });

    test('should display correctly on desktop viewport', async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1280, height: 720 });
      await page.goto('/');
      await page.waitForLoadState('load');

      // Both sidebar and main should be visible
      const sidebar = page.locator('nav');
      const main = page.locator('main').first();
      await expect(sidebar).toBeVisible({ timeout: 10000 });
      await expect(main).toBeVisible({ timeout: 10000 });
    });
  });
});