/**
 * Logs Page Object Model
 *
 * Encapsulates logs page interactions and elements.
 */

import type { Page, Locator } from '@playwright/test';
import { BasePage, SidebarComponent, HeaderComponent } from './base.page';

export class LogsPage extends BasePage {
  readonly sidebar: SidebarComponent;
  readonly header: HeaderComponent;

  // Page elements
  readonly pageTitle: Locator;
  readonly logsContainer: Locator;
  readonly logEntries: Locator;

  constructor(page: Page) {
    super(page);
    this.sidebar = new SidebarComponent(page);
    this.header = new HeaderComponent(page);

    // Page elements - use header title
    this.pageTitle = page.locator('header').locator('h1');

    // Logs container - look for main content area or specific container
    this.logsContainer = page.locator('[data-testid="logs-container"]').or(
      page.locator('.logs-container').or(page.locator('main'))
    );

    // Log entries
    this.logEntries = page.locator('[data-testid="log-entry"]').or(page.locator('.log-entry'));
  }

  /**
   * Navigate to logs page
   */
  async goto() {
    await super.goto('/logs');
    await this.waitForReady();
  }

  /**
   * Wait for logs to appear
   */
  async waitForLogs(timeout = 5000) {
    await this.logsContainer.waitFor({ timeout, state: 'visible' }).catch(() => {
      // Ignore if not found
    });
  }

  /**
   * Get visible log entries
   */
  async getLogEntries(): Promise<string[]> {
    const entries = await this.logEntries.allTextContents();
    return entries;
  }
}