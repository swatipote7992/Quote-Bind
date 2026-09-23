# QuoteBind Frontend — Initial Release

Initial scaffold of the QuoteBind frontend: React + TypeScript + Tailwind CSS, set up to eventually talk to the QuoteBind API (`main.py` / `app/` at the repo root).

## Stack

- **React** 19
- **TypeScript** ~6.0
- **Vite** 8 (build tool / dev server)
- **Tailwind CSS** 4 (via `@tailwindcss/vite`, no separate PostCSS config needed)
- **oxlint** for linting (Vite's current default, replacing ESLint in the template)

## How it was set up

```powershell
cd C:\Users\spote\Projects\backProj\QuoteBind
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install tailwindcss @tailwindcss/vite
```

`vite.config.ts` — added the Tailwind plugin alongside the React plugin:

```ts
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

`src/index.css` — replaced the template's default CSS with a single Tailwind import:

```css
@import 'tailwindcss';
```

`src/App.tsx` — replaced the Vite/React starter page with a minimal placeholder page (Tailwind utility classes only, no custom CSS).

### Removed from the template

- `src/App.css` (superseded by Tailwind)
- `src/assets/` (unused starter images/icons — `hero.png`, `react.svg`, `vite.svg`, and duplicate copies of `favicon.svg`/`icons.svg` not actually referenced by anything)
- `public/icons.svg` (only used by the removed starter page's social/doc links)

Kept `public/favicon.svg`, referenced by `index.html`.

`index.html`'s `<title>` changed from the default `frontend` to `QuoteBind`.

## Running it

```powershell
cd frontend
npm install
npm run dev       # dev server, http://localhost:5173
npm run build     # type-check (tsc -b) + production build to dist/
npm run preview   # serve the production build locally
npm run lint       # oxlint
```

## Verified working

- `npm run build` — type-checks and builds cleanly; Tailwind CSS output confirmed non-empty (8.57 kB), i.e. utility classes are actually being generated, not just an unused import.
- `npm run lint` — clean, no errors.
- Dev server smoke-tested: served `index.html` correctly with the updated `<title>QuoteBind</title>`.

## Not done yet

- No routing, state management, or API client wired up yet — this is purely the base scaffold.
- No connection to the backend API (CORS config on the FastAPI side, base URL/env config on this side) — next step once frontend work starts for real.
- No component library / design system decisions made — `App.tsx`'s placeholder styling is illustrative only.
