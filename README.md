# Scalable API Platform

Production-oriented FastAPI task management API with JWT authentication, async PostgreSQL access, Redis-backed caching, Celery background workers, Alembic migrations, Docker Compose environments, and an nginx production entrypoint.

## Features

- Versioned REST API under `/api/v1`
- User registration, login, refresh tokens, and role-aware user management
- Authenticated task CRUD with pagination, filtering, and Redis cache invalidation
- Async SQLAlchemy models for users and tasks
- Alembic migration workflow
- Celery worker, beat scheduler, and Flower monitoring
- Docker Compose for local development and production-style deployment
- GitHub Actions CI with linting and tests

## Quick Start

```bash
cp .env.example .env
docker compose up --build
docker compose exec api alembic upgrade head
```

Useful URLs:

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`
- Flower: `http://localhost:5555`

## Local Development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
docker compose up postgres redis
alembic upgrade head
uvicorn app.main:app --reload
```

## Environment

Copy `.env.example` to `.env` and replace all defaults before production use.

Important variables:

- `SECRET_KEY`: JWT signing secret. Use a long random value in production.
- `DATABASE_URL`: async SQLAlchemy URL.
- `DATABASE_URL_SYNC`: sync SQLAlchemy URL used by Alembic.
- `REDIS_URL`: Redis database used by the API cache.
- `CELERY_BROKER_URL`: Redis broker URL for Celery.
- `CELERY_RESULT_BACKEND`: Redis result backend URL for Celery.
- `ALLOWED_ORIGINS`: JSON list of browser origins allowed by CORS.

## API Examples

Register:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"ada@example.com","username":"ada","password":"Password123"}'
```

Login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ada@example.com","password":"Password123"}'
```

Create a task:

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Ship API","priority":"high"}'
```

## Tests And Quality

```bash
ruff check .
pytest
```

The test suite expects PostgreSQL and Redis to be available. The GitHub Actions workflow starts both services automatically.

## Migrations

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
alembic downgrade -1
```

## Production Compose

`docker-compose.prod.yml` runs nginx in front of multiple API replicas plus worker, beat, PostgreSQL, Redis, and Flower.

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Before production use:

- Replace every default secret and password.
- Restrict `ALLOWED_ORIGINS`.
- Put PostgreSQL and Redis on managed services or persistent volumes.
- Terminate TLS at a load balancer or extend the nginx config with certificates.
- Run `alembic upgrade head` during deployment.

## Status

This repository is complete enough to build, run, test, and deploy as a baseline scalable API. It remains a starter platform, so production teams should add observability, backup policy, rate limiting, structured logs, and real email/report implementations before public launch.
