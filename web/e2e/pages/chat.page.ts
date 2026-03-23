/**
 * Chat Page Object Model
 *
 * Encapsulates chat page interactions and elements.
 */

import type { Page, Locator, Response } from '@playwright/test';
import { BasePage, SidebarComponent, HeaderComponent } from './base.page';

export class ChatPage extends BasePage {
  readonly sidebar: SidebarComponent;
  readonly header: HeaderComponent;

  // Message input elements
  readonly messageInput: Locator;
  readonly sendButton: Locator;
  readonly stopButton: Locator;

  // Message list elements
  readonly messageList: Locator;
  readonly userMessages: Locator;
  readonly assistantMessages: Locator;

  // Session elements
  readonly newChatButton: Locator;
  readonly emptyState: Locator;

  // Thinking indicator
  readonly thinkingIndicator: Locator;

  constructor(page: Page) {
    super(page);
    this.sidebar = new SidebarComponent(page);
    this.header = new HeaderComponent(page);

    // Message input - based on actual MessageInput component
    // Use textarea with placeholder text as fallback
    this.messageInput = page.locator('textarea').filter({ hasText: '' }).first();
    this.sendButton = page.locator('button[aria-label="Send message"]');
    this.stopButton = page.locator('button[aria-label="Stop streaming"]');

    // Message list - based on ChatSession component
    this.messageList = page.locator('[role="log"], [data-testid="message-list"]').or(page.locator('main').locator('ul'));
    this.userMessages = page.locator('[data-testid="user-message"]').or(page.getByTestId('user-message'));
    this.assistantMessages = page.locator('[data-testid="assistant-message"]').or(page.getByTestId('assistant-message'));

    // Sessions
    this.newChatButton = page.getByRole('button', { name: /new.*chat/i });

    // Empty state from ChatArea component
    this.emptyState = page.locator('text=No messages yet').or(page.getByText('No messages yet'));

    // Thinking indicator
    this.thinkingIndicator = page.locator('text=Thinking');
  }

  /**
   * Navigate to chat page (home page)
   */
  async goto() {
    await super.goto('/');
    await this.waitForReady();
  }

  /**
   * Send a message in the chat
   */
  async sendMessage(message: string): Promise<Response | null> {
    await this.messageInput.fill(message);

    // Set up response promise before clicking send
    const responsePromise = this.page.waitForResponse(
      (resp) => resp.url().includes('/api/chat/message'),
      { timeout: 5000 }
    ).catch(() => null);

    await this.sendButton.click();

    return responsePromise;
  }

  /**
   * Wait for assistant response
   */
  async waitForAssistantResponse(timeout = 10000) {
    await this.page.waitForSelector(
      '[data-testid="assistant-message"], .assistant-message',
      { timeout, state: 'visible' }
    ).catch(() => {
      // Ignore if not found
    });
  }

  /**
   * Get all visible messages
   */
  async getVisibleMessages(): Promise<string[]> {
    const messages = await this.page.locator('[data-testid*="message"], .message').allTextContents();
    return messages;
  }

  /**
   * Check if streaming is in progress
   */
  async isStreaming(): Promise<boolean> {
    const streamingIndicator = this.page.locator('[data-testid="streaming"], .streaming-indicator');
    return await streamingIndicator.isVisible().catch(() => false);
  }

  /**
   * Check if thinking indicator is visible
   */
  async isThinking(): Promise<boolean> {
    return await this.thinkingIndicator.isVisible().catch(() => false);
  }

  /**
   * Create a new chat session
   */
  async createNewChat() {
    await this.newChatButton.click();
  }

  /**
   * Check if empty state is visible
   */
  async isEmptyStateVisible(): Promise<boolean> {
    return await this.emptyState.isVisible().catch(() => false);
  }

  /**
   * Wait for page to be fully loaded
   */
  async waitForPageReady() {
    // Wait for the textarea to be visible using Playwright's auto-waiting
    await this.messageInput.waitFor({ state: 'visible', timeout: 15000 }).catch(() => {
      // If textarea not found, check for empty state
    });
  }
}