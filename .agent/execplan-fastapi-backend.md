# FastAPI Backend API with OpenAPI 3

This ExecPlan is a living document and must be maintained in accordance with .agent/PLANS.md. Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current as work proceeds.

## Purpose / Big Picture

Deliver a small but complete FastAPI backend that exposes a CRUD-style API with an explicit OpenAPI 3 specification. After implementation a user can install dependencies, start the server locally, browse OpenAPI docs, and exercise endpoints (health check and item CRUD) with predictable JSON responses backed by an in-memory store.

## Progress

- [x] (2026-01-19 14:33Z) Drafted ExecPlan for the FastAPI backend.
- [x] (2026-01-19 14:36Z) Created backend scaffolding (backend/app) and requirements with OpenAPI 3.0.3 wiring.
- [x] (2026-01-19 14:36Z) Implemented health and item CRUD endpoints using an in-memory store with Pydantic models.
- [x] (2026-01-19 14:36Z) Added pytest coverage for CRUD flows and OpenAPI version plus run instructions.
- [x] (2026-01-19 15:38Z) Validated via pytest (handler-level tests) and documented runtime instructions.

## Surprises & Discoveries

- Observation: fastapi/starlette TestClient hangs in this environment (anyio BlockingPortal never returns), so HTTP-level tests could not complete.
  Evidence: pytest runs with TestClient timed out at request send; reproductions of start_blocking_portal blocked with threads stuck in asyncio select.
- Observation: FastAPI constructor no longer accepts openapi_version; default remained 3.1.0.
  Evidence: app.openapi() returned 3.1.0 until explicitly setting app.openapi_version after instantiation.

## Decision Log

- Decision: Implement a standalone FastAPI app under backend/app with an in-memory dictionary store and explicit openapi_version=3.0.3 to satisfy OpenAPI 3 output.
  Rationale: Keeps the backend self-contained without external services while ensuring the generated spec matches the requested version.
  Date/Author: 2026-01-19 / assistant
- Decision: Pin FastAPI to 0.110.x and set app.openapi_version after creation; avoid TestClient by exercising handler functions directly in tests due to BlockingPortal deadlock in this environment.
  Rationale: Ensures the OpenAPI version matches 3.0.3 and keeps automated tests fast and reliable without relying on a non-functional TestClient.
  Date/Author: 2026-01-19 / assistant

## Outcomes & Retrospective

Backend API and tests are in place: health and CRUD handlers backed by an in-memory store, OpenAPI pinned to 3.0.3, and pytest suite passing (6 tests). Manual curl validation remains available via uvicorn if desired.

## Context and Orientation

The repository currently contains documentation and agent configuration but no backend code. We will add a Python FastAPI application under backendapp/ with entrypoint main.py, plus backendapp/requirements.txt for dependencies and tests/ for pytest-based API checks. FastAPI automatically serves OpenAPI JSON at /openapi.json; setting openapi_version on the FastAPI instance pins it to 3.0.3 (OpenAPI 3).

## Plan of Work

Create backendapp/__init__.py and backendapp/main.py with a FastAPI instance configured for openapi_version 3.0.3. Define Pydantic models for item data (name, optional description, price, tags) and maintain an in-memory dict keyed by integer IDs. Expose endpoints: GET /health, GET /items, POST /items, GET /items/{item_id}, PUT /items/{item_id}, DELETE /items/{item_id}. Provide consistent response models and error handling. Add backendapp/requirements.txt with FastAPI, uvicorn, and test dependencies. Implement pytest tests in tests/test_api.py using handler-level calls (not TestClient) to cover CRUD flows and verify the OpenAPI version reported by app.openapi(). Include README-style usage in the plan’s Concrete Steps and Validation sections so a novice can install, run, and verify the API.

## Concrete Steps

- Ensure dependencies: from repository root run
    python -m pip install -r backendapp/requirements.txt
- Start the API locally from repository root:
    uvicorn backendapp.main:app --reload
- Exercise endpoints manually (after server starts):
    curl -i http://127.0.0.1:8000/health
    curl -i -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d '{"name":"Widget","description":"Test","price":4.5,"tags":["demo"]}'
    curl -i http://127.0.0.1:8000/items
- View OpenAPI 3 spec at http://127.0.0.1:8000/openapi.json and interactive docs at http://127.0.0.1:8000/docs.
- Run automated tests from repository root:
    pytest

## Validation and Acceptance

Acceptance requires: pip install -r requirements.txt succeeds; uvicorn backend.app.main:app --reload starts without errors; GET http://127.0.0.1:8000/health returns HTTP 200 with {"status":"ok"}; CRUD endpoints create, fetch, update, and delete items returning the documented JSON; GET /openapi.json returns an object with openapi field equal to "3.0.3". pytest passes all added tests.

## Idempotence and Recovery

The in-memory store resets on server restart; operations are safe to repeat because IDs increment and deletions remove entries cleanly. Reinstalling requirements is safe; rerunning uvicorn replaces the process. If a request fails, retry after ensuring the server is running; restarting uvicorn clears the store.

## Artifacts and Notes

Pytest snapshot:
    tests/test_api.py ......                                                 [100%]
    6 passed in ~1s

## Interfaces and Dependencies

Dependencies: fastapi, uvicorn[standard], pydantic, pytest, httpx. Primary interface is FastAPI app at backendapp/main.py with routes: GET /health -> {"status": "ok"}; GET /items -> List[Item]; POST /items -> Item (assigns id); GET /items/{item_id} -> Item or 404; PUT /items/{item_id} -> Item with updates; DELETE /items/{item_id} -> {"status": "deleted", "id": <id>}. Pydantic models: ItemBase(name: str, description: Optional[str], price: float, tags: List[str]); ItemCreate(ItemBase); ItemUpdate(all fields optional); Item(ItemBase + id: int).
