# C# Backend API (ASP.NET Core)

This ExecPlan is a living document and must be maintained in accordance with .agent/PLANS.md. Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current.

## Purpose / Big Picture

Build a small ASP.NET Core minimal API exposing health and item CRUD endpoints with OpenAPI 3 docs. After completion, `dotnet test` passes and `dotnet run --project csharp-backend/BackendApi.csproj` serves `/health`, `/items`, and `/swagger/v1/swagger.json` containing OpenAPI metadata.

## Progress

- [x] (2026-01-20 07:36Z) Drafted ExecPlan.
- [x] (2026-01-20 07:36Z) Scaffolded ASP.NET Core project under csharp-backend/ with Swagger/OpenAPI deps.
- [x] (2026-01-20 07:36Z) Implemented health + item CRUD with in-memory store.
- [x] (2026-01-20 07:36Z) Added xUnit + WebApplicationFactory tests for health, CRUD, and OpenAPI presence.
- [x] (2026-01-20 07:37Z) Ran dotnet test; all tests passing.

## Surprises & Discoveries

- NuGet restore required network; once allowed, restore and tests passed.

## Decision Log

- Decision: Use ASP.NET Core minimal APIs with Swashbuckle for OpenAPI and in-memory concurrent store.
  Rationale: Small footprint, built-in OpenAPI support, easy to test via WebApplicationFactory.
  Date/Author: 2026-01-20 / assistant

## Outcomes & Retrospective

API implemented and validated via tests. Minimal API with Swagger, in-memory CRUD, and integration tests are all passing. Manual run remains to exercise curl if desired.

## Context and Orientation

No C# web backend exists yet. We will add `csharp-backend/` with `BackendApi.csproj`, `Program.cs`, `Models/Item*.cs`, `Services/ItemStore.cs`. Tests live in `csharp-backend.Tests/` with xUnit + WebApplicationFactory for integration-style checks. API mirrors other backends: `/health`, `/items`, `/items/{id}`; OpenAPI JSON at `/swagger/v1/swagger.json`.

## Plan of Work

1) Create `csharp-backend/BackendApi.csproj` targeting net9.0; add packages Microsoft.AspNetCore.OpenApi and Swashbuckle.AspNetCore. 2) Implement Program.cs with minimal API endpoints for health + CRUD, add Swagger, and mark `public partial class Program` for tests. 3) Add models (ItemRequest, ItemUpdate, ItemResponse) and in-memory ItemStore. 4) Add tests in `csharp-backend.Tests/` validating health, CRUD, and swagger openapi field via WebApplicationFactory. 5) Run `dotnet test` and note run instructions (`dotnet run --project csharp-backend/BackendApi.csproj`).

## Concrete Steps

- Scaffold project files in csharp-backend/: BackendApi.csproj, Program.cs, Models/Item*.cs, Services/ItemStore.cs.
- Scaffold test project csharp-backend.Tests/ with reference to backend, packages (xunit, Microsoft.AspNetCore.Mvc.Testing).
- Implement endpoints:
  - GET `/health` -> {status:"ok"}
  - GET `/items` -> list
  - POST `/items` -> create (201)
  - GET `/items/{id}` -> item or 404
  - PUT `/items/{id}` -> update or 404
  - DELETE `/items/{id}` -> {"status":"deleted","id":id} or 404
- Commands: `dotnet test` (solution root), run app: `dotnet run --project csharp-backend/BackendApi.csproj`.

## Validation and Acceptance

Acceptance: `dotnet test` passes; running the app serves endpoints above; `/swagger/v1/swagger.json` returns JSON with an `openapi` field; CRUD behaves correctly (create, list, get, update, delete).

## Idempotence and Recovery

In-memory store resets on restart. Re-running dotnet build/test is safe. If restore fails due to network, retry with network access.

## Artifacts and Notes

Test snapshot:
    dotnet test csharp-backend.Tests/csharp-backend.Tests.csproj
    Passed! - Failed: 0, Passed: 3, Skipped: 0

## Interfaces and Dependencies

Dependencies: ASP.NET Core minimal APIs, Swashbuckle.AspNetCore, Microsoft.AspNetCore.OpenApi, xUnit + Microsoft.AspNetCore.Mvc.Testing for tests. Public types: ItemRequest, ItemUpdate, ItemResponse, ItemStore (in-memory). Endpoints at root path as described.
