/**
 * Playwright Test Fixtures
 *
 * Custom fixtures for E2E testing with page objects.
 */

import { test as base } from '@playwright/test';
import { ChatPage } from '../pages/chat.page';
import { SkillsPage } from '../pages/skills.page';
import { SettingsPage } from '../pages/settings.page';
import { LogsPage } from '../pages/logs.page';

// Define custom fixtures
type MyFixtures = {
  chatPage: ChatPage;
  skillsPage: SkillsPage;
  settingsPage: SettingsPage;
  logsPage: LogsPage;
};

// Extend base test with custom fixtures
export const test = base.extend<MyFixtures>({
  chatPage: async ({ page }, use) => {
    const chatPage = new ChatPage(page);
    await use(chatPage);
  },

  skillsPage: async ({ page }, use) => {
    const skillsPage = new SkillsPage(page);
    await use(skillsPage);
  },

  settingsPage: async ({ page }, use) => {
    const settingsPage = new SettingsPage(page);
    await use(settingsPage);
  },

  logsPage: async ({ page }, use) => {
    const logsPage = new LogsPage(page);
    await use(logsPage);
  },
});

// Export expect for convenience
export { expect } from '@playwright/test';