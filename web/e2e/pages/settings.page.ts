/**
 * Settings Page Object Model
 *
 * Encapsulates settings page interactions and elements.
 */

import type { Page, Locator } from '@playwright/test';
import { BasePage, SidebarComponent, HeaderComponent } from './base.page';

export class SettingsPage extends BasePage {
  readonly sidebar: SidebarComponent;
  readonly header: HeaderComponent;

  // Page elements
  readonly pageTitle: Locator;
  readonly generalSettingsCard: Locator;

  // Settings elements
  readonly themeSetting: Locator;
  readonly languageSetting: Locator;
  readonly themeValue: Locator;
  readonly languageValue: Locator;

  constructor(page: Page) {
    super(page);
    this.sidebar = new SidebarComponent(page);
    this.header = new HeaderComponent(page);

    // Page elements - use header title
    this.pageTitle = page.locator('header').locator('h1');

    // General settings card
    this.generalSettingsCard = page.locator('main').filter({ hasText: /settings/i });

    // Settings - look for labels
    this.themeSetting = page.getByText(/theme/i).first();
    this.languageSetting = page.getByText(/language/i).first();
    this.themeValue = page.locator('.text-muted-foreground').first();
    this.languageValue = page.locator('.text-muted-foreground').nth(1);
  }

  /**
   * Navigate to settings page
   */
  async goto() {
    await super.goto('/settings');
    await this.waitForReady();
  }

  /**
   * Wait for settings to load
   */
  async waitForSettingsToLoad(timeout = 10000) {
    await this.pageTitle.waitFor({ timeout, state: 'visible' });
  }

  /**
   * Get current theme value
   */
  async getThemeValue(): Promise<string | null> {
    return await this.themeValue.textContent();
  }

  /**
   * Get current language value
   */
  async getLanguageValue(): Promise<string | null> {
    return await this.languageValue.textContent();
  }

  /**
   * Check if settings card is visible
   */
  async isSettingsVisible(): Promise<boolean> {
    return await this.generalSettingsCard.isVisible().catch(() => false);
  }
}