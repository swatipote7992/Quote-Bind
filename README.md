# QuoteBind

A FastAPI service for managing insurance product quotes: a product catalog, a
question catalog, per-product question sets, and the quotes that tie an
applicant to a product and its answered question set.

## Tech stack

- **Python** 3.13
- **FastAPI** for the HTTP API
- **SQLAlchemy** (Core + ORM) for the data layer
- **PostgreSQL** as the database
- **Uvicorn** as the ASGI server

## Prerequisites

- Python 3.13+
- PostgreSQL running locally (or reachable over the network)

## 1. Clone the repo

```bash
git clone <repo-url>
cd QuoteBind
```

## 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run this once (per machine):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**Windows (Git Bash) / macOS / Linux:**

```bash
python -m venv .venv
source .venv/Scripts/activate   # Git Bash on Windows
# or
source .venv/bin/activate       # macOS / Linux
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Set up the database

Create a PostgreSQL database (default name used by this project is
`QuoteBindAdmin`):

```sql
CREATE DATABASE "QuoteBindAdmin";
```

The connection string is read from the `DATABASE_URL` environment variable
(via a `.env.local` file, loaded with `python-dotenv`). Copy the example
file and fill in your own credentials:

```bash
cp .env.local.example .env.local
```

```
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/QuoteBindAdmin
```

`.env.local` is gitignored, so your credentials never get committed — only
`.env.local.example` (with placeholder values) is tracked in the repo.

Tables are created automatically the first time the app starts
(`Base.metadata.create_all(bind=engine)` in `main.py`), so no separate
`CREATE TABLE` step is needed for a fresh database.

### Seed data (optional)

Sample data — products, questions, question sets, applicants, and quotes —
is provided as SQL scripts in `app/database/scripts/`, meant to be run in
order against a freshly created (empty) database:

| Script | Seeds |
|---|---|
| `001_seed_question_sets.sql` | `product_catalog`, `question_catalog`, and a `question_set` per product |
| `002_seed_applicants.sql` | 10 sample applicants |
| `003_seed_quotes.sql` | 30 sample quotes (3 per applicant, across distinct products) |
| `005_seed_more_quotes.sql` | 70 additional randomized quotes (bringing the total to 100), useful for exercising pagination |

Run them with `psql`:

```bash
psql -U <user> -d QuoteBindAdmin -f app/database/scripts/001_seed_question_sets.sql
psql -U <user> -d QuoteBindAdmin -f app/database/scripts/002_seed_applicants.sql
psql -U <user> -d QuoteBindAdmin -f app/database/scripts/003_seed_quotes.sql
psql -U <user> -d QuoteBindAdmin -f app/database/scripts/005_seed_more_quotes.sql
```

Note: `product_id` and `question_id` are `SERIAL`, so `001_seed_question_sets.sql`
relies on insertion order to land on the ids the seed data references (see
the comment at the top of that file). Run it against an empty
`product_catalog` / `question_catalog`, or adjust the ids in the script to
match what's already there.

## 5. Run the API

```bash
fastapi dev main.py
```

or, equivalently:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive API docs (Swagger UI) are auto-generated at:

```
http://127.0.0.1:8000/docs
```

(ReDoc is available at `/redoc`.)

## API reference

### Products — `/products`

| Method | Path | Description |
|---|---|---|
| GET | `/products/` | List all products |
| GET | `/products/{product_id}` | Get a product by id |
| POST | `/products/` | Create a product |
| PUT | `/products/{product_id}` | Update a product |
| DELETE | `/products/{product_id}` | Delete a product |

Create/update body:

```json
{
  "product_label": "Audi",
  "isActive": true
}
```

### Questions — `/questions`

| Method | Path | Description |
|---|---|---|
| GET | `/questions/` | List all catalog questions |
| GET | `/questions/page?page=&page_size=` | List catalog questions with offset pagination |
| GET | `/questions/{question_id}` | Get a question by id |
| POST | `/questions/` | Create a question |
| PUT | `/questions/{question_id}` | Update a question |
| DELETE | `/questions/{question_id}` | Delete a question |

Create/update body:

```json
{
  "question_label": "Are you 18 years old?",
  "default_answer": "Yes"
}
```

#### Pagination

`GET /questions/page` returns a page of results along with pagination
metadata, instead of the full list:

| Query param | Default | Constraints |
|---|---|---|
| `page` | `1` | `>= 1` |
| `page_size` | `10` | `1` to `50` |

Response body:

```json
{
  "data": [
    { "question_id": 1, "question_label": "Are you 18 years old?", "default_answer": "Yes" }
  ],
  "page": 1,
  "page_size": 10,
  "total": 42,
  "total_pages": 5
}
```

```bash
curl "http://127.0.0.1:8000/questions/page?page=2&page_size=10"
```

### Quotes — `/quotes`

| Method | Path | Description |
|---|---|---|
| GET | `/quotes/` | List all quotes |
| GET | `/quotes/search?name=&category=` | Search quotes by applicant name and/or product label |
| GET | `/quotes/page?after=&limit=` | List quotes with keyset (cursor) pagination |
| GET | `/quotes/{quote_id}` | Get a quote by id |
| POST | `/quotes/` | Create a quote |
| PUT | `/quotes/{quote_id}` | Update a quote |
| DELETE | `/quotes/{quote_id}` | Delete a quote (also removes its applicant) |

Create/update body :

`product_id` must reference an existing product; the
quote's `question_set` is resolved automatically from that product's linked
question set:

```json
{
  "product_id": 1,
  "applicant": {
    "applicant_id": 9001,
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@example.com",
    "phone": "7700900999",
    "date_of_birth": "1990-01-01"
  }
}
```

#### Pagination

`GET /quotes/page` returns a page of quotes using keyset (cursor)
pagination instead of the full list. Quotes are ordered by `id` ascending;
`after` is the `id` of the last quote seen on the previous page (omit it to
get the first page), and `limit` caps how many quotes come back:

| Query param | Default | Constraints |
|---|---|---|
| `after` | `null` | Must be an existing quote `id` |
| `limit` | `10` | `1` to `50` |

Response body:

```json
{
  "data": [
    { "id": "Q001", "status": "New", "product_id": 1, "applicant": { "...": "..." }, "question_set": [], "created_at": "...", "updated_at": "..." }
  ],
  "next_cursor": "Q010",
  "has_more": true
}
```

`next_cursor` is the `id` to pass as `after` on the next request; it's
`null` once `has_more` is `false`. Unlike offset pagination, this stays
correct even if rows are inserted or deleted between requests.

```bash
curl "http://127.0.0.1:8000/quotes/page?limit=10"
curl "http://127.0.0.1:8000/quotes/page?after=Q010&limit=10"
```

## Example: try it with curl

```bash
# List products
curl http://127.0.0.1:8000/products/

# Create a quote for product_id 1 (Audi)
curl -X POST http://127.0.0.1:8000/quotes/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "applicant": {
      "applicant_id": 9001,
      "first_name": "Jane",
      "last_name": "Doe",
      "email": "jane.doe@example.com",
      "phone": "7700900999",
      "date_of_birth": "1990-01-01"
    }
  }'
```

## Error handling

Errors that aren't already `HTTPException`s raised directly in a service
(e.g. the plain 404s/409s like `"Product not found"` or `"This Product
already exist"`) are caught centrally by global exception handlers in
`app/api/exception_handlers.py`, registered once on startup via
`register_exception_handler(app)` in `main.py`:

| Exception | Status | Response body |
|---|---|---|
| `UnknownProductIdError` (raised from `quote_repository.py` when a quote references a `product_id` that doesn't exist) | `404` | `{"detail": "Unknown product_id: <id>"}` |
| `sqlalchemy.exc.IntegrityError` (e.g. deleting a product/question still referenced elsewhere) | `409` | `{"detail": "Cannot delete: this record is still referenced by another record"}` |
| Any other unhandled exception | `500` | `{"detail": "Internal Server Error"}` |

The `500` case logs the full traceback server-side (see Logging below) —
the client only ever sees the generic message, never internal details.

## Logging

Configured once at startup in `main.py` via `logging.basicConfig(...)`,
writing to **`app.log`** in the project root (not the console) at `INFO`
level and above, formatted as:

```
%(asctime)s %(levelname)s %(name)s: %(message)s
```

The global exception handlers (`app/api/exception_handlers.py`) log as
they run:

- `WARNING` for expected/handled error conditions — an unknown
  `product_id`, or an `IntegrityError` on delete — including the request
  method/path (and the offending id, where relevant).
- `ERROR` for any unhandled exception, via `logger.exception(...)`, which
  includes the full traceback — this is the only place a real bug's stack
  trace is captured, so check `app.log` first when a `500` shows up.

`app.log` is written relative to wherever the app is started from and
isn't tracked in git.

### Azure Monitor / Application Insights (optional)

Logs (and traces/metrics) can additionally be forwarded to Azure Monitor
via the [Azure Monitor OpenTelemetry
Distro](https://pypi.org/project/azure-monitor-opentelemetry/)
(`azure-monitor-opentelemetry` in `requirements.txt`). This is entirely
optional and off by default — `app.log` keeps working the same either way.

To enable it, set `APPLICATIONINSIGHTS_CONNECTION_STRING` in `.env.local`
(see `.env.local.example` for the placeholder format) to a real
Application Insights connection string from the Azure portal. `main.py`
checks for that env var at startup and, only if it's present, calls
`configure_azure_monitor()` before the app is created:

```python
if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    from azure.monitor.opentelemetry import configure_azure_monitor
    configure_azure_monitor(logger_name="")
```

`logger_name=""` attaches to the Python root logger, so every logger in
the app (including the exception handlers' `WARNING`/`ERROR` logs above)
gets mirrored to Azure, not just a specific named one.

**Known caveat**: with this enabled, app startup can take significantly
longer (tens of seconds) — the SDK's Azure resource detector tries to
reach Azure's Instance Metadata Service to identify the hosting
environment, which has to time out first on any machine that isn't
actually running in Azure (i.e. local dev). You may also see benign
`"recursive logging"` guard messages from the SDK's own internal
diagnostics — not errors. Because of the startup cost, leave this env var
unset for local development unless you're actively testing against a real
Application Insights resource.

## Project structure

```
app/
  api/routes/        FastAPI routers (products, questions, quotes)
  api/exception_handlers.py  Global exception handlers (see Error handling)
  database/          DB engine/session setup + seed scripts
  models/            SQLAlchemy models
  schemas/           Pydantic request/response schemas
  repositories/      Data-access layer
  services/          Business logic layer
main.py              App entrypoint
requirements.txt     Python dependencies
```
