/**
 * Base Page Object Model
 *
 * Provides common functionality for all page objects.
 */

import type { Page, Locator } from '@playwright/test';

export abstract class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Navigate to a specific path
   */
  async goto(path: string = '/') {
    await this.page.goto(path);
  }

  /**
   * Wait for page to be ready
   */
  async waitForReady() {
    // Use 'load' instead of 'networkidle' for faster, more reliable waiting
    await this.page.waitForLoadState('load');
  }

  /**
   * Take a screenshot
   */
  async screenshot(name: string) {
    await this.page.screenshot({ path: `test-results/${name}.png` });
  }
}

/**
 * Sidebar Page Object
 */
export class SidebarComponent {
  readonly page: Page;
  readonly navChat: Locator;
  readonly navSkills: Locator;
  readonly navLogs: Locator;
  readonly navSettings: Locator;
  readonly brand: Locator;

  constructor(page: Page) {
    this.page = page;
    this.navChat = page.getByRole('link', { name: 'Chat' });
    this.navSkills = page.getByRole('link', { name: 'Skills' });
    this.navLogs = page.getByRole('link', { name: 'Logs' });
    this.navSettings = page.getByRole('link', { name: 'Settings' });
    this.brand = page.locator('nav').getByText('Markwritter');
  }

  async navigateToChat() {
    await this.navChat.click();
  }

  async navigateToSkills() {
    await this.navSkills.click();
  }

  async navigateToLogs() {
    await this.navLogs.click();
  }

  async navigateToSettings() {
    await this.navSettings.click();
  }
}

/**
 * Header Page Object
 */
export class HeaderComponent {
  readonly page: Page;
  readonly title: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator('header').getByRole('heading');
  }

  async getTitle(): Promise<string | null> {
    return await this.title.textContent();
  }
}