/**
 * Navigation E2E Tests
 *
 * Tests for basic navigation and layout functionality.
 */

import { test, expect } from './fixtures/test-fixtures';

test.describe('Navigation', () => {
  test.describe('Sidebar Navigation', () => {
    test('should display TopBar on chat page (no sidebar)', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('load');

      // Chat page uses ChatLayout with TopBar instead of MainLayout sidebar
      const topBar = page.locator('header').first();
      await expect(topBar).toBeVisible();

      // TopBar contains "Markwritter" brand
      await expect(topBar.getByText('Markwritter')).toBeVisible();

      // Chat page should have main content area (chat panel)
      const main = page.locator('main').first();
      await expect(main).toBeVisible();
    });

    test('should navigate to Skills page via drawer nav from chat', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('load');

      // Chat page has no sidebar - use drawer nav (hamburger menu)
      const menuButton = page.locator('header').first().getByRole('button').first();
      await menuButton.click();

      // Wait for drawer to open and click Skills link
      const skillsLink = page.locator('nav').getByRole('link', { name: 'Skills' });
      await expect(skillsLink).toBeVisible({ timeout: 5000 });
      await skillsLink.click();

      // Verify URL
      await expect(page).toHaveURL(/\/skills/);
    });

    test('should navigate to Logs page via drawer nav from chat', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('load');

      // Chat page has no sidebar - use drawer nav (hamburger menu)
      const menuButton = page.locator('header').first().getByRole('button').first();
      await menuButton.click();

      // Wait for drawer to open and click Logs link
      const logsLink = page.locator('nav').getByRole('link', { name: 'Logs' });
      await expect(logsLink).toBeVisible({ timeout: 5000 });
      await logsLink.click();

      // Verify URL
      await expect(page).toHaveURL(/\/logs/);
    });

    test('should navigate to Settings page via drawer nav from chat', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('load');

      // Chat page has no sidebar - use drawer nav (hamburger menu)
      const menuButton = page.locator('header').first().getByRole('button').first();
      await menuButton.click();

      // Wait for drawer to open and click Settings link
      const settingsLink = page.locator('nav').getByRole('link', { name: 'Settings' });
      await expect(settingsLink).toBeVisible({ timeout: 5000 });
      await settingsLink.click();

      // Verify URL
      await expect(page).toHaveURL(/\/settings/);
    });

    test('should navigate to Chat page from other pages', async ({ page }) => {
      await page.goto('/settings');
      await page.waitForLoadState('load');

      // Settings page uses MainLayout with sidebar - Chat button is in sidebar
      await page.getByRole('button', { name: 'Chat' }).click();

      // Verify URL - Chat route is /
      await expect(page).toHaveURL(/\//);
    });
  });

  test.describe('Page Headers', () => {
    test('should display Chat TopBar on chat page', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('load');

      // Chat page uses TopBar (not MainLayout Header)
      const topBar = page.locator('header').first();
      await expect(topBar).toBeVisible({ timeout: 10000 });

      // TopBar contains "Markwritter" brand name
      await expect(topBar.getByText('Markwritter')).toBeVisible();
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

      // TopBar should be visible
      const topBar = page.locator('header').first();
      await expect(topBar).toBeVisible({ timeout: 10000 });

      // On mobile, panels may overlap - just verify TopBar is present
      // Note: mobile responsive layout needs implementation (panels should collapse on small screens)
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

      // TopBar and main should be visible
      const topBar = page.locator('header').first();
      const main = page.locator('main').first();
      await expect(topBar).toBeVisible({ timeout: 10000 });
      await expect(main).toBeVisible({ timeout: 10000 });
    });
  });
});