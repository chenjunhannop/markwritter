# Markwritter Web Frontend

Next.js 15 frontend for Markwritter - an AI-native knowledge management tool.

## Features

- **Query Interface**: Natural language search and semantic retrieval
- **Record Interface**: Note editor with AI assistance
- **Explore Interface**: Knowledge graph visualization

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 15.x | App Router, SSR |
| React | 19.x | UI components |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.x | Styling |
| Zustand | 5.x | State management |
| Radix UI | latest | Accessible components |
| React Markdown | 10.x | Markdown rendering |
| Lucide React | latest | Icons |

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm (recommended)

### Installation

```bash
pnpm install
```

### Development

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

### Build

```bash
pnpm build
pnpm start
```

## Project Structure

```
web/
├── app/              # Next.js App Router pages
│   ├── page.tsx      # Home page
│   ├── layout.tsx    # Root layout
│   ├── globals.css   # Global styles
│   └── api/          # API routes
├── components/       # React components
│   └── ui/           # Shadcn/UI components
├── lib/              # Utilities and helpers
├── hooks/            # Custom React hooks
├── e2e/              # Playwright E2E tests
└── public/           # Static assets
```

## Testing

### Unit Tests

```bash
pnpm test
pnpm test:run
pnpm test:coverage
```

### E2E Tests

```bash
pnpm test:e2e
pnpm test:e2e:ui      # Interactive UI mode
pnpm test:e2e:debug   # Debug mode
pnpm test:e2e:headed  # Run with browser visible
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` by default.

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/query` | POST | Search and query notes |
| `/api/record` | POST | Create/update notes |
| `/api/explore` | GET | Get knowledge graph data |
| `/api/chat` | WS | Real-time conversation |

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

### Docker

```bash
docker build -f Dockerfile.web -t markwritter-web .
docker run -p 3000:3000 markwritter-web
```

### Vercel

The easiest deployment method:

```bash
vercel deploy
```

## Related Documentation

- [Main Project README](../README.md)
- [Project Overview](../docs/OVERVIEW.md)
- [Transformation Plan](../note/note-app-transformation-plan.md)