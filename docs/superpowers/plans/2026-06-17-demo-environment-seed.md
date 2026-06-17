# Demo Environment and Seed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a separate Docker demo/staging instance and a guarded fake-data seed that cannot run against production by default.

**Architecture:** Keep the real `indufor` service unchanged and add an optional compose override for `indufor_demo`. Add seed logic under `backend/app/seed/demo_data.py` so it can be run with `python -m app.seed.demo_data` from the backend container. Extend `/health` with optional `EXPECTED_DB_NAME` checking without exposing connection strings.

**Tech Stack:** FastAPI, SQLAlchemy ORM, PyMySQL/MySQL, pytest, Docker Compose.

---

### Task 1: Seed Safety Contract

**Files:**
- Create: `backend/app/seed/__init__.py`
- Create: `backend/app/seed/demo_data.py`
- Test: `backend/tests/test_demo_seed.py`

- [ ] **Step 1: Write failing tests** for production abort, missing `ALLOW_DEMO_SEED`, no secret output, and fake demo names.
- [ ] **Step 2: Run** `python -m pytest backend/tests/test_demo_seed.py -q` and verify failures are because `app.seed.demo_data` is missing.
- [ ] **Step 3: Implement minimal seed guards** reading `APP_ENV`, `APP_INSTANCE`, `ALLOW_DEMO_SEED`, and `DEMO_SEED_RECORDS`.
- [ ] **Step 4: Add deterministic fake demo data** for users, personal, mobiles, places, predios, rodales, process/mobile types, business units, production rows, fuel rows, and assignments.
- [ ] **Step 5: Run** `python -m pytest backend/tests/test_demo_seed.py -q`.

### Task 2: Health Expected Database Check

**Files:**
- Modify: `backend/app/core/config.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_app.py`

- [ ] **Step 1: Write failing tests** for `EXPECTED_DB_NAME` matching and mismatch in `/health`.
- [ ] **Step 2: Run** `python -m pytest backend/tests/test_app.py -q` and verify the new tests fail because the payload lacks the DB-name check.
- [ ] **Step 3: Add `EXPECTED_DB_NAME` setting** and query `DATABASE()` when configured.
- [ ] **Step 4: Return only safe fields** such as `expected`, `actual`, and `matches`; never return `DATABASE_URL`.
- [ ] **Step 5: Run** `python -m pytest backend/tests/test_app.py -q`.

### Task 3: Demo Compose and Environment Docs

**Files:**
- Create: `docker-compose.demo.yml`
- Modify: `backend/.env.example`
- Modify: `README_DEPLOY.md`
- Create: `docs/DEMO_ENVIRONMENT.md`

- [ ] **Step 1: Add optional compose override** with `indufor_demo` on `127.0.0.1:18104`.
- [ ] **Step 2: Add demo/staging variables** to `.env.example`.
- [ ] **Step 3: Document DB creation, env-file setup, container startup, seed execution, and validation curls.**
- [ ] **Step 4: Include a clear warning to never run the demo seed against a real DB.**

### Task 4: Final Verification and Commit

**Files:**
- Review all changed files.

- [ ] **Step 1: Run targeted backend tests.**
- [ ] **Step 2: Run `docker compose -f docker-compose.yml -f docker-compose.demo.yml config` if Docker Compose is available.**
- [ ] **Step 3: Confirm no real `.env` files were modified and no secrets are printed.**
- [ ] **Step 4: Commit as `Add demo environment and fake data seed`.**
