# Java Backend API (Spring Boot)

This ExecPlan is a living document and must be maintained in accordance with .agent/PLANS.md. Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current.

## Purpose / Big Picture

Deliver a Java backend using Spring Boot (the most widely used Java web framework) exposing a small CRUD API (health + items) with OpenAPI documentation. After implementation a user can `mvn test`, `mvn spring-boot:run`, hit `/health` and `/items` and see an OpenAPI JSON at `/v3/api-docs`.

## Progress

- [x] (2026-01-20 01:00Z) Drafted ExecPlan.
- [x] (2026-01-20 07:27Z) Scaffolded Spring Boot project with dependencies (web, validation, springdoc) under java-backend/.
- [x] (2026-01-20 07:27Z) Implemented health + item CRUD (in-memory) with DTOs/service.
- [x] (2026-01-20 07:27Z) Added MockMvc tests for health, CRUD, and OpenAPI availability.
- [ ] Run mvn test and document manual run steps; update retrospective.

## Surprises & Discoveries

- Observation: Maven CLI not present in environment (`mvn: command not found`), so tests/build were not executed here.
  Evidence: running `cd java-backend && mvn test` failed with shell error.

## Decision Log

- Decision: Use Spring Boot (most popular Java framework) + springdoc-openapi for REST + OpenAPI with in-memory Map store and AtomicInteger IDs.
  Rationale: Lightweight to stand up, widely understood, auto-exposes OpenAPI, no external DB needed.
  Date/Author: 2026-01-20 / assistant

## Outcomes & Retrospective

Backend code and tests are in place; validation awaits Maven availability. Once Maven is installed or wrapper added, run `mvn test` and `mvn spring-boot:run` to complete acceptance.

## Context and Orientation

No Java backend exists yet. New project will live in `java-backend/` with `pom.xml`, `src/main/java/com/example/backend/...` for application, controller, service, models, and `src/test/java/...` for tests. API paths mirror the Python backend: `/health`, `/items`, `/items/{id}`. OpenAPI JSON available at `/v3/api-docs` via springdoc.

## Plan of Work

1) Create Maven project in `java-backend/` targeting Java 21; dependencies: spring-boot-starter-web, spring-boot-starter-validation, springdoc-openapi-starter-webmvc-ui, spring-boot-starter-test. 2) Implement models: ItemRequest, ItemUpdate, ItemResponse. 3) Implement ItemService with in-memory Map + AtomicInteger. 4) Implement ItemController with REST endpoints (health + CRUD) using @Valid. 5) Add tests with MockMvc verifying health, create/list/get/update/delete, and that `/v3/api-docs` returns JSON containing `openapi`. 6) Run `mvn test` and document run commands (`mvn spring-boot:run`).

## Concrete Steps

- Create `java-backend/pom.xml` with dependencies above; set Java version 21.
- Add application class `BackendApplication` and packages `controller`, `service`, `model`.
- Implement endpoints: GET `/health` -> `{"status":"ok"}`; GET `/items`; POST `/items`; GET `/items/{id}`; PUT `/items/{id}`; DELETE `/items/{id}`.
- Write tests in `src/test/java/com/example/backend/ItemControllerTests.java` using MockMvc to cover health and CRUD flow; assert `/v3/api-docs` contains `openapi`.
- Commands: from repo root `cd java-backend && mvn test`; run app with `mvn spring-boot:run`.

## Validation and Acceptance

Acceptance: `mvn test` passes; running `mvn spring-boot:run` starts server without errors; GET `/health` returns 200/{"status":"ok"}; CRUD endpoints behave correctly; `/v3/api-docs` returns OpenAPI JSON containing an `openapi` field.

## Idempotence and Recovery

In-memory store resets on restart. Maven builds are repeatable. If dependencies fail to download, retry with network access. Adjust port/conflicts via `server.port` if needed.

## Artifacts and Notes

Capture test output and any manual curl results after validation.

## Interfaces and Dependencies

Interfaces: REST endpoints under root path, models in `com.example.backend.model`. Dependencies: Spring Boot web/validation, springdoc-openapi, JUnit/MockMvc for tests. Configurable env: `SERVER_PORT` if desired via Spring config.
