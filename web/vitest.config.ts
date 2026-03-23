import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'e2e/**'],
    globals: true,
    setupFiles: ['./test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: [
        'lib/**/*.ts',
        'hooks/**/*.ts',
        'components/chat/**/*.{ts,tsx}',
        'components/layout/**/*.{ts,tsx}',
        'components/skills/**/*.{ts,tsx}',
      ],
      exclude: [
        'lib/**/*.test.ts',
        'lib/**/*.spec.ts',
        'components/**/*.test.tsx',
        'components/**/*.spec.tsx',
        'components/layout/index.ts',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },
});