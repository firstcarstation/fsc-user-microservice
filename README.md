# fsc-user-microservice

User identity, authentication, KYC, address, and role management. PostgreSQL database `user_db`. Dependencies managed with [uv](https://github.com/astral-sh/uv).

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- PostgreSQL

## Setup

1. **Virtual environment and install**

```bash
uv venv
uv sync
```

2. **Environment**

```bash
cp .env.example .env
```

Set `DATABASE_URL` (e.g. `postgresql+psycopg2://user:password@localhost:5432/user_db`) and `JWT_SECRET_KEY`.

## Database

Create the database and run migrations:

```bash
createdb user_db
uv run alembic upgrade head
```

## Run

```bash
uv run uvicorn app.main:app --reload
```

API base: `http://127.0.0.1:8000`. Docs: `http://127.0.0.1:8000/docs`.

## Add dependency

```bash
uv add <package_name>
```

Commit `pyproject.toml` and `uv.lock`.

## Repository structure

```
fsc-user-microservice/
├── app/
│   ├── main.py
│   ├── api/api_v1/routes.py, endpoints/
│   ├── core/ (config, logging, security, database, exceptions)
│   ├── models/ (addresses, roles, persons, users, logins, hubs, enums)
│   ├── schemas/
│   ├── crud/command/, crud/query/
│   └── services/
├── alembic/ (env.py, script.py.mako, versions/)
├── tests/
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
└── README.md
```

## Schema (user_db)

Core tables: **addresses**, **roles**, **persons**, **users**, **logins**. **hubs** (minimal) for user assignment. All primary/foreign keys `varchar(36)`. Enums: `user_status_enum`, `role_type_enum`.
