# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

Two independent projects in one repo, run and tested separately:

- `backend/` — FastAPI service (Python 3.13, SQLAlchemy, PostgreSQL).
- `frontend/` — React 19 + TypeScript app (Vite, MUI, MUI X DataGrid).

The frontend talks to the backend over HTTP (`VITE_API_BASE_URL`, default
`http://localhost:8000`); there's no shared build tooling between them.

## Commands

### Backend (run from `backend/`)

```bash
python -m venv .venv
source .venv/Scripts/activate      # Git Bash on Windows; .venv/bin/activate on macOS/Linux
pip install -r requirements.txt

cp .env.local.example .env.local   # then set DATABASE_URL (and optionally
                                    # APPLICATIONINSIGHTS_CONNECTION_STRING)

fastapi dev main.py                # dev server at http://127.0.0.1:8000, docs at /docs
# or: uvicorn main:app --reload

pytest app/test -q                                           # all tests
pytest app/test/unit/services/test_quote_service.py -q        # one file
pytest app/test/unit/services/test_quote_service.py::test_create_quote_passes_answers_to_repository -q  # one test
```

`pytest` must be run from `backend/` — `testpaths = ["app/test"]` is set in
`backend/pyproject.toml`, relative to that directory.

Tables are created automatically on startup (`Base.metadata.create_all` in
`main.py`); optional seed data lives in `app/database/scripts/*.sql` and must
be run in numeric filename order with `psql` against an empty database (see
`README.md` for the exact commands — the ids are `SERIAL` and the
scripts rely on insertion order to line up with the ids later scripts
reference).

### Frontend (run from `frontend/`)

```bash
npm install
npm run dev          # dev server at http://localhost:5173
npm run build         # tsc -b && vite build (type-checks, then builds)
npm run lint          # oxlint
npm test              # jest, all tests
npm run test:watch
npx jest test/pages/QuoteFormPage.test.tsx   # one file
npx jest -t "name substring"                 # by test name
```

`VITE_API_BASE_URL` is read from `frontend/.env.local` (see
`frontend/.env.example`).

## Linting & code style

### Backend

No formatter or linter is configured — no `ruff`/`black`/`flake8`/`mypy`
in `requirements.txt` or any config file (a stray `.mypy_cache/` at the
repo root is leftover from a manual run, not a configured tool). Match
the surrounding code by hand:

- Full type hints on function signatures, modern `X | None` syntax
  (not `Optional[X]`).
- One file per domain per layer (`quote_service.py`, `quote_repository.py`,
  `quotes_router.py`, …) — a new domain follows the same three-file shape.
- Repository-private helpers are prefixed `_` (`_to_document`,
  `_build_answers`).
- Docstrings are rare; a short `#` comment above the non-obvious line is
  the norm instead of docstrings on every function.
- Tests are plain `pytest` functions (no test classes), named
  `test_<behavior being verified>`, with a `_service_with_mock_repo()` /
  `_applicant_payload()`-style private helper at the top of the file for
  shared setup.

### Frontend

`npm run lint` runs `oxlint` (config: `frontend/.oxlintrc.json` — `react`,
`typescript`, `oxc` plugins, plus `react/rules-of-hooks` as an error and
`react/only-export-components` as a warning on top of oxlint's defaults).
Formatting is handled by Prettier (config: `frontend/.prettierrc.json`;
`npm run format` writes, `npm run format:check` verifies), plus the
conventions already in the code:

- No semicolons, single quotes, 2-space indent.
- Components are `export function ComponentName() { ... }` — not
  `export default`, not an arrow-function const.
- Component styling goes through MUI's `sx` prop, not separate CSS or
  `styled-components`; Tailwind utility classes are reserved for the page
  chrome in `src/layout/`.
- `tsconfig.app.json` sets `noUnusedLocals`, `noUnusedParameters`,
  `noFallthroughCasesInSwitch`, and `erasableSyntaxOnly` — the last one
  means no real TS `enum`s or parameter-property constructors; model a
  fixed set of values as a string-literal union type instead (see
  `QuoteStatusDto` in `src/types/quote_model.ts`).
- `npm run build` runs `tsc -b` before `vite build`, so a type error fails
  the build, not just the editor.

## Architecture

### Backend: router → service → repository, dict documents in between

Each domain (`products`, `questions`, `quotes`) has one file per layer:
`app/api/routes/*_router.py` → `app/services/*_service.py` →
`app/repositories/*_repository.py`. All SQLAlchemy models live in one file,
`app/models/quote_model.py`. Pydantic request/response schemas live
separately under `app/schemas/*.py` and are kept in sync with the models by
hand.

Repositories never hand ORM objects up to callers: each has a
`_to_document()` method that converts a loaded row (with its relations
already joined) into a plain `dict`. Services and routers work with those
dicts and with the Pydantic schemas, not with ORM instances.

### Sessions: opened per repository method, not injected

Repository methods each open their own `with SessionLocal() as db:` block.
`app/api/dependencies.py` defines a `get_db` / `DbDependency` FastAPI
dependency, but nothing in the routers actually uses it — it's exercised
only by its own test.

### Centralized error handling — exceptions must propagate, not be caught

Domain exceptions (`UnknownProductIdError`, `UnknownQuestionIdError` in
`app/repositories/quote_repository.py`) are raised from repositories and
deliberately left uncaught by the service/router layers — this is enforced
by tests named `test_*_does_not_catch_unknown_*_error`. They're converted to
HTTP responses only by the global handlers registered once via
`register_exception_handler(app)` in `main.py`
(`app/api/exception_handlers.py`):

| Exception | Status |
|---|---|
| `UnknownProductIdError` | 404 |
| `UnknownQuestionIdError` | 422 |
| `sqlalchemy.exc.IntegrityError` | 409 |
| anything else | 500 (logged with traceback to `app.log`) |

### Quotes: product → question_set → question_array → question_catalog

A product has one `QuestionSet` (1:1), linked to `question_catalog` rows via
the `question_array` join table. `GET /products/{id}/questions` resolves
that chain. A quote's `question_set` in API responses carries both
`default_answer` (the catalog's value at save time) and `answer` (what was
actually given), stored per-question in the `quote_answer` table. On
create/update: a question left out of the `answers` array falls back to the
catalog default; an answer for a question outside the product's question set
raises `UnknownQuestionIdError` (422); changing a quote's `product_id`
re-resolves and resets its answers unless new `answers` are supplied in the
same request. Quotes saved before `quote_answer` existed have no rows there,
so `_question_documents()` falls back to listing the product's current
questions each answered with its default.

### Applicants: one new row per create, not deduplicated

`applicant_ref_id` is a caller-supplied business id, not a unique key.
`POST /quotes/` always creates a new `Applicant` row, even if another quote
already used the same `applicant_ref_id` — so the same ref id can end up on
several distinct rows. `PUT /quotes/{id}` updates the quote's existing
`Applicant` row in place rather than creating a new one. Deleting a quote
deletes its own `Applicant` row. Don't assume one ref id maps to one row
when writing a migration or a bulk edit against this table.

### Quote id generation is sequential, not max-based

`QuoteService.create_quote` derives the new id as
`Q{len(existing_quotes) + 1:03d}` — based on the current row count, not
`max(id)`. After any delete, the next create can collide with an id that
still exists.

### Backend test layers

- `app/test/unit/services/` — service logic only; the repository is a
  `MagicMock`.
- `app/test/integration/repositories/` — real SQL against an in-memory
  SQLite DB; `app/test/integration/conftest.py`'s `db_session` fixture
  monkeypatches each repository module's `SessionLocal`, so these need no
  real Postgres.
- `app/test/api/routes/` — `TestClient` against a single router, with that
  domain's `Service` class patched (e.g.
  `patch("app.api.routes.quotes_router.QuoteService")`) — exercises request
  validation and the global exception handlers end-to-end.
- `app/test/schemas/` — Pydantic validators in isolation.

### Frontend: per-domain api / types / component / page

Each domain has a matching `src/api/*.ts` (thin wrappers around
`src/api/client.ts`'s `apiGet`/`apiPost`/`apiPut`/`apiDelete`),
`src/types/*_model.ts` (hand-written, comment-linked to the backend schema
it mirrors), `src/components/*DataGrid.tsx` (MUI X DataGrid), and
`src/pages/*Page.tsx`. Quotes additionally has
`src/pages/QuoteFormPage.tsx`, shared by both `/quotes/new` and
`/quotes/:quoteId/edit` (routed in `src/App.tsx`), which tells create and
edit apart by whether the `:quoteId` param is present.

Data grids and forms are built from MUI (`@mui/material`,
`@mui/x-data-grid`); Tailwind utility classes are used only for the outer
page chrome (`src/layout/Header.tsx`, `Footer.tsx`, `Layout.tsx`).

### Frontend test environment
Jest only looks under
`frontend/test/`, mirroring `frontend/src/` in path and filename.
