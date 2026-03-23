/**
 * Skills Page Object Model
 *
 * Encapsulates skills page interactions and elements.
 */

import type { Page, Locator } from '@playwright/test';
import { BasePage, SidebarComponent, HeaderComponent } from './base.page';

export class SkillsPage extends BasePage {
  readonly sidebar: SidebarComponent;
  readonly header: HeaderComponent;

  // Page elements
  readonly pageTitle: Locator;
  readonly newSkillButton: Locator;
  readonly searchInput: Locator;
  readonly clearSearchButton: Locator;
  readonly skillCount: Locator;

  // Skill list elements
  readonly skillListContainer: Locator;
  readonly skillCards: Locator;
  readonly loadingSpinner: Locator;
  readonly errorMessage: Locator;
  readonly emptyState: Locator;

  constructor(page: Page) {
    super(page);
    this.sidebar = new SidebarComponent(page);
    this.header = new HeaderComponent(page);

    // Page elements - use header title
    this.pageTitle = page.locator('header').locator('h1');

    // New Skill button is a link
    this.newSkillButton = page.getByRole('link', { name: /new skill/i });

    // Search input
    this.searchInput = page.getByPlaceholder(/search.*skills/i);

    // Clear search button
    this.clearSearchButton = page.getByRole('button', { name: /clear search/i });

    // Skill count
    this.skillCount = page.locator('.text-muted-foreground').filter({ hasText: /skill/i });

    // Skill list - use data-testid or fallback
    this.skillListContainer = page.getByTestId('skill-list-container').or(page.locator('main'));
    this.skillCards = page.getByTestId('skill-card').or(page.locator('li').filter({ has: page.locator('h3') }));

    // Loading spinner - look for Loader2 animation
    this.loadingSpinner = page.locator('[role="status"]').or(page.locator('.animate-spin'));

    // Error alert
    this.errorMessage = page.getByRole('alert');

    // Empty state
    this.emptyState = page.getByText(/no skills/i);
  }

  /**
   * Navigate to skills page
   */
  async goto() {
    await super.goto('/skills');
    await this.waitForReady();
  }

  /**
   * Wait for skills to load
   */
  async waitForSkillsToLoad(timeout = 15000) {
    // Wait for either skills to appear or loading to complete
    try {
      await this.page.waitForFunction(
        () => {
          const loading = document.querySelector('.animate-spin');
          const skills = document.querySelectorAll('[data-testid="skill-card"]');
          const skillItems = document.querySelectorAll('li h3');
          const emptyState = document.body.textContent?.includes('No skills');
          return !loading || skills.length > 0 || skillItems.length > 0 || emptyState;
        },
        { timeout }
      );
    } catch {
      // Ignore timeout - component may have already loaded
    }
  }

  /**
   * Search for skills
   */
  async searchSkills(query: string) {
    await this.searchInput.fill(query);
    await this.page.waitForTimeout(300); // Wait for debounce
  }

  /**
   * Clear search
   */
  async clearSearch() {
    await this.clearSearchButton.click();
  }

  /**
   * Get all visible skill names
   */
  async getSkillNames(): Promise<string[]> {
    const cards = await this.skillCards.all();
    const names: string[] = [];
    for (const card of cards) {
      const title = await card.locator('h3, [class*="CardTitle"], [class*="font-semibold"]').textContent();
      if (title) names.push(title);
    }
    return names;
  }

  /**
   * Get skill count text
   */
  async getSkillCount(): Promise<string | null> {
    return await this.skillCount.textContent();
  }

  /**
   * Click on a skill card to view details
   */
  async clickSkillCard(skillName: string) {
    await this.skillCards
      .filter({ hasText: skillName })
      .getByRole('link', { name: /run/i })
      .click();
  }

  /**
   * Click run button on a skill card
   */
  async runSkill(skillName: string) {
    await this.skillCards
      .filter({ hasText: skillName })
      .getByRole('button', { name: /run/i })
      .click();
  }

  /**
   * Click edit button on a skill card
   */
  async editSkill(skillName: string) {
    await this.skillCards
      .filter({ hasText: skillName })
      .getByRole('button', { name: /edit/i })
      .click();
  }

  /**
   * Check if loading
   */
  async isLoading(): Promise<boolean> {
    return await this.loadingSpinner.isVisible().catch(() => false);
  }

  /**
   * Check if there's an error
   */
  async hasError(): Promise<boolean> {
    return await this.errorMessage.isVisible().catch(() => false);
  }

  /**
   * Get error message
   */
  async getErrorMessage(): Promise<string | null> {
    return await this.errorMessage.textContent();
  }

  /**
   * Click retry button after error
   */
  async retryLoading() {
    await this.page.getByRole('button', { name: /retry/i }).click();
  }
}