# GitHub Copilot Usage (Workspace)

- Enable workspace instructions in VS Code and point to `.copilot/INSTRUCTIONS.md`.
- Prompts available under `.copilot/prompts/`:
  - `implement.md`: follow scope → plan → change → report.
  - `review.md`: findings-first review guidance.
  - `tests.md`: focused test authoring.
- Context hints: `.copilot/context.json` lists key files (backendapp/main.py, frontend/src, batch-csharp/*, .agent/*).
- Common commands for grounding suggestions:
  - Backend: `uvicorn backendapp.main:app --reload`
  - Frontend: `cd frontend && npm run dev` (build: `npm run build`)
  - Python tests: `python -m pytest`
  - .NET tests: `dotnet test batch-csharp.Tests/Batch-csharp.Tests.csproj`
- Keep requests concise; mention relevant files/paths to help Copilot pull the right context.
