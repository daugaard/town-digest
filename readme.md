# Town Digest

A calm, chronological civic digest for local communities.  

Town Digest collects newsletters and announcements from local organizations, extracts structured events and general news, and publishes a chronological news feed and event calendar for each town — without algorithms, engagement metrics, or social media noise.

---

## Motivation

Local information has become fragmented:

- Local newspapers are shrinking or disappearing.
- Schools, clubs, libraries, and municipalities send updates through separate newsletters.
- Town information lives in inboxes, PDFs, and scattered mailing lists.
- Social media amplifies noise and outrage, not community relevance.

Town Digest provides a neutral, structured, opt-in infrastructure for towns to stay informed.

---

## Features (MVP)

- Accepts newsletters via email forwarding (opt-in).  
- Extracts:
  - Structured events (date, time, location)  
  - General news/announcements  
- Publishes chronological news feed and event calendar.  
- Links to original source for transparency.  
- Minimal, calm design with optional small interactivity.

---

## Architecture

The main components of this application include:
- IMAP inbox for email ingestion
- Prefect for data pipeline
- Flask for web application
  - DaisyUI design system
- SQLAlchemy for data access
- Alembic for database migrations

## Developement Environment

To get started install dependencies:
```bash
uv sync
```

Install frontend dependencies:
```bash
npm install
```

Then you can run the development server:
```bash
uv run honcho start
```

With everything running you can access the main web interface on http://localhost:5000 and the Prefect UI on http://localhost:4200.

## Linting

Run Ruff across the codebase:
```bash
uv run ruff check .
```

Auto-fix where safe:
```bash
uv run ruff check . --fix
```

Format (if we enable formatting rules later):
```bash
uv run ruff format .
```

## Database Migrations

Create a new migration:
```bash
uv run alembic revision --autogenerate -m "describe change"
```

Apply migrations:
```bash
uv run alembic upgrade head
```

## Development Seed Data

Load baseline development configuration data (create-only; command raises if records already exist):
```bash
uv run flask --app src/town_digest/app/main.py seed-dev
```

Typical reset flow:
```bash
uv run alembic upgrade head
uv run flask --app src/town_digest/app/main.py seed-dev
```

## Database Connection

Application runtime and Alembic both read the connection string from `DATABASE_URL` via
`town_digest.config.load_settings()`.

Example:
```bash
export DATABASE_URL="postgresql+psycopg://town_digest_user:somepw@localhost/town_digest_dev"
```
