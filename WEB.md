Frontend (Next.js at repository root)

- Dev: npm install && npm run dev
- Open http://localhost:3000
- The upload form posts to /api/analyze (Python function). If deploying the API separately, set NEXT_PUBLIC_API_BASE to the API origin.

Environment
- NEXT_PUBLIC_API_BASE: optional; when set, frontend uses `${NEXT_PUBLIC_API_BASE}/api/analyze`.

shadcn/ui
- To integrate, add Tailwind CSS and run shadcn CLI to generate components.
- I can wire Tailwind + shadcn on request.

