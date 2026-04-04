/**
 * Navigation E2E Tests
 *
 * Tests for basic navigation and layout functionality.
 */

import { test, expect } from './fixtures/test-fixtures';

test.describe('Navigation', () => {
  test.describe('Sidebar Navigation', () => {
    test('should display sidebar on chat page', async ({ page }) => {
      await page.goto('/chat');
      await page.waitForLoadState('load');

      // All pages share the same Sidebar + Header
      const sidebar = page.locator('nav').first();
      await expect(sidebar).toBeVisible();

      // Sidebar contains nav items
      await expect(sidebar.getByRole('button', { name: 'Chat' })).toBeVisible();
      await expect(sidebar.getByRole('button', { name: 'Settings' })).toBeVisible();

      // Header shows page title
      const header = page.locator('header').first();
      await expect(header).toBeVisible();
      await expect(header.getByRole('heading', { name: 'Chat' })).toBeVisible();
    });

    test('should navigate to Skills page via sidebar from chat', async ({ page }) => {
      await page.goto('/chat');
      await page.waitForLoadState('load');

      // Click Skills button in sidebar
      await page.getByRole('button', { name: 'Skills' }).click();

      // Verify URL
      await expect(page).toHaveURL(/\/skills/);
    });

    test('should navigate to Logs page via sidebar from chat', async ({ page }) => {
      await page.goto('/chat');
      await page.waitForLoadState('load');

      // Click Logs button in sidebar
      await page.getByRole('button', { name: 'Logs' }).click();

      // Verify URL
      await expect(page).toHaveURL(/\/logs/);
    });

    test('should navigate to Settings page via sidebar from chat', async ({ page }) => {
      await page.goto('/chat');
      await page.waitForLoadState('load');

      // Click Settings button in sidebar
      await page.getByRole('button', { name: 'Settings' }).click();

      // Verify URL
      await expect(page).toHaveURL(/\/settings/);
    });

    test('should navigate to Chat page from other pages', async ({ page }) => {
      await page.goto('/settings');
      await page.waitForLoadState('load');

      // Chat button is in sidebar
      await page.getByRole('button', { name: 'Chat' }).click();

      // Verify URL
      await expect(page).toHaveURL(/\/chat/);
    });
  });

  test.describe('Page Headers', () => {
    test('should display Chat header on chat page', async ({ page }) => {
      await page.goto('/chat');
      await page.waitForLoadState('load');

      // All pages share Header with page title
      const header = page.locator('header').first();
      await expect(header).toBeVisible({ timeout: 10000 });

      // Header shows "Chat" title
      await expect(header.getByRole('heading', { name: 'Chat' })).toBeVisible();
    });

    test('should display Skills header on skills page', async ({ skillsPage }) => {
      // Mock API to avoid errors
      await skillsPage.page.route('**/api/v1/skills/**', async (route) => {
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

      // Header should be visible
      const header = page.locator('header').first();
      await expect(header).toBeVisible({ timeout: 10000 });

      // On mobile, verify header is present
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

      // Header and main should be visible
      const header = page.locator('header').first();
      const main = page.locator('main').first();
      await expect(header).toBeVisible({ timeout: 10000 });
      await expect(main).toBeVisible({ timeout: 10000 });
    });
  });
});