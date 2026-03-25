/**
 * Tests for ResultsList Component
 *
 * Tests the search results display component including:
 * - Result rendering
 * - Empty state
 * - Loading state
 * - Error state
 * - Click handling
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ResultsList } from './results-list';
import type { SearchResult } from '@/lib/query-api';

// Mock the query store
let mockStoreState = {
  searchResults: [] as SearchResult[],
  isSearching: false,
  searchError: null as string | null,
  searchQuery: '',
};

vi.mock('@/lib/query-store', () => ({
  useQueryStore: vi.fn((selector: (state: typeof mockStoreState) => unknown) =>
    selector(mockStoreState)
  ),
}));

describe('ResultsList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockStoreState = {
      searchResults: [],
      isSearching: false,
      searchError: null,
      searchQuery: '',
    };
  });

  describe('Rendering', () => {
    it('should render empty state when no results', () => {
      render(<ResultsList />);

      // When no search query, shows initial message
      expect(screen.getByText(/enter a search query/i)).toBeInTheDocument();
    });

    it('should show no results message when search has no results', () => {
      mockStoreState = {
        ...mockStoreState,
        searchQuery: 'nonexistent',
      };

      render(<ResultsList />);

      expect(screen.getByText(/no results found/i)).toBeInTheDocument();
    });

    it('should render search results', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Test Note',
            content: 'Test content',
            score: 0.95,
          },
          {
            id: '2',
            title: 'Another Note',
            content: 'More content',
            score: 0.85,
          },
        ],
      };

      render(<ResultsList />);

      expect(screen.getByText('Test Note')).toBeInTheDocument();
      expect(screen.getByText('Another Note')).toBeInTheDocument();
    });

    it('should show loading state', () => {
      mockStoreState = {
        ...mockStoreState,
        isSearching: true,
      };

      render(<ResultsList />);

      expect(screen.getByText(/searching/i)).toBeInTheDocument();
    });

    it('should show error state', () => {
      mockStoreState = {
        ...mockStoreState,
        searchError: 'Search failed',
      };

      render(<ResultsList />);

      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(screen.getByText('Search failed')).toBeInTheDocument();
    });
  });

  describe('Result Display', () => {
    it('should display result title', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'My Note Title',
            content: 'Content',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      expect(screen.getByText('My Note Title')).toBeInTheDocument();
    });

    it('should display result score', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Note',
            content: 'Content',
            score: 0.95,
          },
        ],
      };

      render(<ResultsList />);

      expect(screen.getByText(/95%/)).toBeInTheDocument();
    });

    it('should display result content preview', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Note',
            content: 'This is a long content that should be truncated...',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      expect(screen.getByText(/This is a long content/)).toBeInTheDocument();
    });

    it('should display highlighted content if available', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Note',
            content: 'Original content',
            highlighted: '<mark>highlighted</mark> content',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      // The highlighted content should be rendered
      expect(screen.getByText(/highlighted/)).toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    it('should call onResultClick when result is clicked', () => {
      const onResultClick = vi.fn();

      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Clickable Note',
            content: 'Content',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList onResultClick={onResultClick} />);

      fireEvent.click(screen.getByText('Clickable Note'));

      expect(onResultClick).toHaveBeenCalled();
    });

    it('should handle keyboard navigation', () => {
      const onResultClick = vi.fn();

      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'First Note',
            content: 'Content',
            score: 0.9,
          },
          {
            id: '2',
            title: 'Second Note',
            content: 'Content',
            score: 0.8,
          },
        ],
      };

      render(<ResultsList onResultClick={onResultClick} />);

      const firstResult = screen.getByText('First Note').closest('button');
      firstResult?.focus();

      // Press Enter to select
      fireEvent.keyDown(firstResult!, { key: 'Enter' });

      expect(onResultClick).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Note',
            content: 'Content',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      expect(screen.getByRole('list', { name: /search results/i })).toBeInTheDocument();
    });

    it('should have accessible result items', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Accessible Note',
            content: 'Content',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      expect(screen.getAllByRole('listitem')).toHaveLength(1);
    });
  });

  describe('Security - XSS Prevention', () => {
    it('should sanitize script tags from highlighted content', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Test Note',
            content: 'Test content',
            highlighted: '<script>alert("XSS")</script>safe content',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      // Script tag should not be present in the document
      expect(document.querySelector('script')).toBeNull();
    });

    it('should sanitize onclick handlers from highlighted content', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Test Note',
            content: 'Test content',
            highlighted: '<span onclick="alert(\'XSS\')">click me</span>',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      // No element should have onclick attribute
      const elementsWithOnclick = document.querySelectorAll('[onclick]');
      expect(elementsWithOnclick.length).toBe(0);
    });

    it('should sanitize javascript: URLs from highlighted content', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Test Note',
            content: 'Test content',
            highlighted: '<a href="javascript:alert(\'XSS\')">link</a>',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      // Links should not have javascript: href
      const links = document.querySelectorAll('a[href^="javascript:"]');
      expect(links.length).toBe(0);
    });

    it('should sanitize iframe injection attempts', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Test Note',
            content: 'Test content',
            highlighted: '<iframe src="https://evil.com"></iframe>safe text',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      // iframe should be removed
      expect(document.querySelector('iframe')).toBeNull();
    });

    it('should sanitize img onerror handlers', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Test Note',
            content: 'Test content',
            highlighted: '<img src="x" onerror="alert(\'XSS\')">',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      // No element should have onerror attribute
      const elementsWithOnerror = document.querySelectorAll('[onerror]');
      expect(elementsWithOnerror.length).toBe(0);
    });

    it('should preserve safe HTML elements after sanitization', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Test Note',
            content: 'Test content',
            highlighted: '<mark>highlighted</mark> and <strong>bold</strong> text',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      // Safe elements should be preserved
      expect(document.querySelector('mark')).not.toBeNull();
      expect(document.querySelector('strong')).not.toBeNull();
    });

    it('should handle empty highlighted content safely', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Test Note',
            content: 'Test content',
            highlighted: '',
            score: 0.9,
          },
        ],
      };

      const { container } = render(<ResultsList />);

      // Should render without errors
      expect(container).toBeDefined();
    });

    it('should sanitize event handlers from all elements', () => {
      const maliciousHighlight = `
        <div onmouseover="alert('XSS')">hover me</div>
        <button onload="alert('XSS')">click</button>
        <body onpageshow="alert('XSS')">
      `;
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Test Note',
            content: 'Test content',
            highlighted: maliciousHighlight,
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      // No element should have event handler attributes
      const elementsWithEventHandlers = document.querySelectorAll(
        '[onmouseover], [onload], [onpageshow]'
      );
      expect(elementsWithEventHandlers.length).toBe(0);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty title gracefully', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: '',
            content: 'Content',
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      // Should show untitled placeholder
      expect(screen.getByText(/untitled/i)).toBeInTheDocument();
    });

    it('should handle very long content', () => {
      const longContent = 'A'.repeat(500);

      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          {
            id: '1',
            title: 'Note',
            content: longContent,
            score: 0.9,
          },
        ],
      };

      render(<ResultsList />);

      // Content should be truncated
      const contentElement = screen.getByText(/A+/);
      expect(contentElement.textContent?.length).toBeLessThan(500);
    });

    it('should show results count', () => {
      mockStoreState = {
        ...mockStoreState,
        searchResults: [
          { id: '1', title: 'Note 1', content: 'Content', score: 0.9 },
          { id: '2', title: 'Note 2', content: 'Content', score: 0.8 },
          { id: '3', title: 'Note 3', content: 'Content', score: 0.7 },
        ],
        searchQuery: 'test',
      };

      render(<ResultsList />);

      expect(screen.getByText(/3 results/i)).toBeInTheDocument();
    });
  });
});