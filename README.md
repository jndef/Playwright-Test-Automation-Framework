# API Test Automation Framework

REST API test automation framework built on top of [QA Automation Sandbox](https://github.com/manikosto/qa-automation-sandbox).

## Stack
- Python 3.12
- pytest + Allure
- Requests (custom request builder, shared `Session`)
- Pydantic (response validation)
- PostgreSQL (direct DB assertions alongside API assertions)
- Docker / docker-compose
- GitHub Actions (CI)

## Architecture
- `auth/` — authentication, per-role token caching, multi-role service factory
- `services/` — API service layer: endpoints, request payloads/params, response models.
  12 services: admin, auth, bookmarks, comments, follows, likes, messages,
  notifications, posts, search, upload, users
- `common/` — shared HTTP layer: `BaseAPI`, request builder, base param dataclasses
- `fixtures/` — pytest fixtures (API-level and DB-level setup/teardown)
- `tests/` — test suites, one file per service
- `utils/` — test data generation, DB helper, Allure helper, logging
- `config/` — base test class, DB config, stage/environment config
- `pytest.ini` — markers and run configuration

## Setup

### 1. Start the application under test
The framework runs against [QA Automation Sandbox](https://github.com/manikosto/qa-automation-sandbox) —
clone it separately and start it with Docker:
```bash
git clone https://github.com/manikosto/qa-automation-sandbox
cd qa-automation-sandbox
docker-compose up --build
```
This starts the frontend, backend, PostgreSQL and pgweb that the tests run against.

### 2. Configure this repository
```bash
git clone https://github.com/jndef/API-test-automation-framework
cd API-test-automation-framework
cp .env.example .env
```
Fill in `.env`:
- `STAGE` — `local` (points at `http://localhost:8000`)
- Credentials for each role (`ADMIN_*`, `MODERATOR_*`, `USER_BOB_*`, ...) — must match the users seeded in the sandbox
- `ROLES` — list of role aliases used by the framework
- `DB_*` — connection details for the sandbox's PostgreSQL

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## How to run

### Locally
```bash
pytest
```
Markers, verbosity and Allure output path are pre-configured in `pytest.ini`.
Run a specific suite with a marker, e.g.:
```bash
pytest -m smoke
```

### In Docker
```bash
docker-compose up smoke-api-test
```
Runs the suite in a container against `STAGE`/`SUITE`/`THREADS` from `.env`. Generate an HTML Allure report from the results:
```bash
docker-compose up report
```

### CI
`.github/workflows/tests.yml` runs the suite on demand (`workflow_dispatch`) with a
selectable marker and thread count, and publishes the Allure report to GitHub Pages
with history preserved across runs.

## Features
- Multi-role service factory with per-role token caching
- Request builder on top of a shared `requests.Session` (connection reuse)
- Pydantic response validation for every endpoint
- Direct PostgreSQL assertions alongside API-level assertions
- Readable Allure parameters for custom dataclasses (no repr noise)
- Parametrized boundary and negative test data: pagination limits, invalid params,
  file upload validation (size, extension, content-type mismatches)