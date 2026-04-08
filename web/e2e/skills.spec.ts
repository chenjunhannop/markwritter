/**
 * Skills Page E2E Tests
 *
 * Tests for skills API integration and UI functionality.
 */

import { test, expect } from './fixtures/test-fixtures';

// Mock skill data matching the backend API response
const mockSkills = [
  {
    name: 'write-article',
    description: 'Write a blog article on a given topic',
    version: '1.0.0',
    inputs: [
      { name: 'topic', type: 'string', description: 'Article topic', required: true },
      { name: 'length', type: 'number', description: 'Word count', required: false, default: 500 },
    ],
    output: { type: 'string', description: 'Generated article' },
  },
  {
    name: 'summarize',
    description: 'Summarize a given text',
    version: '1.2.0',
    inputs: [
      { name: 'text', type: 'string', description: 'Text to summarize', required: true },
    ],
    output: { type: 'string', description: 'Summary of the text' },
  },
];

test.describe('Skills Page', () => {
  test.describe('Page Load', () => {
    test('should load skills page successfully', async ({ skillsPage }) => {
      await skillsPage.page.route('**/api/v1/skills/**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSkills),
        });
      });

      await skillsPage.goto();

      // Verify URL
      await expect(skillsPage.page).toHaveURL(/\/skills/);
    });

    test('should display page title', async ({ skillsPage }) => {
      await skillsPage.page.route('**/api/v1/skills/**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSkills),
        });
      });

      await skillsPage.goto();

      // Check header title
      const header = skillsPage.page.locator('header');
      await expect(header).toBeVisible();

      const title = header.locator('h1');
      await expect(title).toContainText('Skill');
    });

    test('should display skills list', async ({ skillsPage }) => {
      await skillsPage.page.route('**/api/v1/skills/**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSkills),
        });
      });

      await skillsPage.goto();

      // Skills list should be visible
      const skillList = skillsPage.page.locator('ul, [role="list"]').first();
      await expect(skillList).toBeVisible();
    });
  });

  test.describe('Skills List', () => {
    test('should display skills from API', async ({ skillsPage }) => {
      // Mock the skills API
      await skillsPage.page.route('**/api/v1/skills/**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSkills),
        });
      });

      await skillsPage.goto();
      await skillsPage.waitForSkillsToLoad();

      // Verify skills are displayed - skill cards are rendered
      const skillCards = skillsPage.page.locator('[data-testid="skill-card"]').or(
        skillsPage.page.locator('li').filter({ hasText: 'write-article' })
      );
      const count = await skillCards.count();
      expect(count).toBeGreaterThan(0);
    });

    test('should display skill card with correct information', async ({ skillsPage }) => {
      await skillsPage.page.route('**/api/v1/skills/**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSkills),
        });
      });

      await skillsPage.goto();
      await skillsPage.waitForSkillsToLoad();

      // Check that skill name is displayed
      const skillName = skillsPage.page.getByText('write-article').first();
      await expect(skillName).toBeVisible();
    });
  });

  test.describe('Search Functionality', () => {
    test('should have search input', async ({ skillsPage }) => {
      await skillsPage.page.route('**/api/v1/skills/**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSkills),
        });
      });

      await skillsPage.goto();

      // Search input has placeholder "Search skills..."
      const searchInput = skillsPage.page.getByPlaceholder(/search.*skills/i);
      await expect(searchInput).toBeVisible();
    });

    test('should filter skills by search query', async ({ skillsPage }) => {
      await skillsPage.page.route('**/api/v1/skills/**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockSkills),
        });
      });

      await skillsPage.goto();
      await skillsPage.waitForSkillsToLoad();

      // Search for a specific skill
      const searchInput = skillsPage.page.getByPlaceholder(/search.*skills/i);
      await searchInput.fill('write');

      // Wait for filtering
      await skillsPage.page.waitForTimeout(500);

      // Verify filtering worked - should still show write-article
      const writeArticle = skillsPage.page.getByText('write-article');
      const isVisible = await writeArticle.isVisible().catch(() => false);
      expect(isVisible).toBe(true);
    });
  });

  test.describe('Error Handling', () => {
    test('should display error message when API fails', async ({ page }) => {
      // Set up route BEFORE navigating
      await page.route('**/api/v1/skills/**', async (route) => {
        await route.fulfill({
          status: 500,
          body: 'Internal Server Error',
        });
      });

      // Navigate after route is set up
      await page.goto('/skills');

      // Should show error alert
      const errorAlert = page.getByRole('alert');
      await expect(errorAlert).toBeVisible({ timeout: 15000 });
    });

    // Skip this test due to SSR + API mock timing issues
    test.skip('should have retry button on error', async ({ page }) => {
      let callCount = 0;

      await page.route('**/api/v1/skills/**', async (route) => {
        callCount++;
        if (callCount === 1) {
          await route.fulfill({
            status: 500,
            body: 'Internal Server Error',
          });
        } else {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockSkills),
          });
        }
      });

      await page.goto('/skills');

      // Wait for error alert
      const errorAlert = page.getByRole('alert');
      await expect(errorAlert).toBeVisible({ timeout: 15000 });

      // Click retry button
      const retryButton = page.getByRole('button', { name: /retry/i });
      await retryButton.click();

      // Wait for skills to load
      await page.waitForTimeout(2000);

      // Verify second API call was made
      expect(callCount).toBeGreaterThanOrEqual(2);
    });
  });

  test.describe('Empty State', () => {
    // Skip this test due to SSR + API mock timing issues
    test.skip('should show empty state when no skills', async ({ page }) => {
      await page.route('**/api/v1/skills/**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      });

      await page.goto('/skills');

      // Wait for loading to complete
      await page.waitForFunction(
        () => {
          const loading = document.querySelector('.animate-spin');
          return !loading;
        },
        { timeout: 15000 }
      );

      // Should show empty state message
      const emptyMessage = page.getByText(/no skills/i);
      await expect(emptyMessage).toBeVisible({ timeout: 15000 });
    });
  });
});