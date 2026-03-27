# C# Batch Processor (High-volume Batch)

This ExecPlan is a living document and must be maintained in accordance with .agent/PLANS.md. Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current.

## Purpose / Big Picture

Deliver a high-volume, parallelized C# batch runner that can process large item sets efficiently with bounded channels, configurable parallelism, and observable progress. After implementation, a user can `dotnet run --project batch-csharp/BatchRunner.csproj` to process hundreds of thousands of items, adjust throughput via flags or env vars, and verify behavior with automated tests.

## Progress

- [x] (2026-01-20 00:07Z) Drafted ExecPlan and implemented batch processor + tests.
- [x] (2026-01-20 00:43Z) Manually validated runtime with sample batch run; documented outputs.

## Surprises & Discoveries

- Observation: Environment only had .NET 9 shared runtime; retargeted projects from net8.0 to net9.0 to run tests/build.
  Evidence: Testhost complained about missing Microsoft.NETCore.App 8.0.0 until retargeting; dotnet test succeeded on net9.0.

## Decision Log

- Decision: Use Channel + worker fan-out with configurable degree of parallelism and reporting cadence.
  Rationale: Bounded channels provide backpressure; Task.Run with cancellation keeps implementation simple and portable.
  Date/Author: 2026-01-20 / assistant
- Decision: Keep simulated work delay pluggable (TimeSpan) and accept config via CLI flags/env vars for count, parallelism, report intervals, and channel capacity.
  Rationale: Allows easy tuning for different batch sizes and environments without code changes.
  Date/Author: 2026-01-20 / assistant
- Decision: Switch target frameworks to net9.0 for app and tests.
  Rationale: Matches available runtime in environment and unblocks test execution.
  Date/Author: 2026-01-20 / assistant

## Outcomes & Retrospective

Batch app and tests are implemented and passing on net9.0. Parallel processing, bounded channel ingestion, progress logging, and basic error capture are in place. Additional manual runs can be documented after any further verification with real workloads.
Manual check processed 2,000 items at 0ms simulated work and reported progress correctly.

## Context and Orientation

Batch code lives in `batch-csharp/` with `BatchRunner.csproj`, `Program.cs`, and `BatchProcessor.cs`. Tests live in `batch-csharp.Tests/` using xUnit. The processor uses `Channel<T>` to feed work to a configurable number of worker tasks. Configuration is provided via CLI flags (`--count`, `--parallel`, `--report-every`, `--work-ms`, `--channel-capacity`) or env vars (`BATCH_COUNT`, `BATCH_PARALLEL`, `BATCH_REPORT_EVERY`, `BATCH_WORK_MS`, `BATCH_CHANNEL_CAPACITY`). `ProcessItemAsync` currently simulates work; replace with real logic for production.

## Plan of Work

1) Create batch-csharp/BatchRunner.csproj (Exe) and implement Program.cs to parse settings, generate WorkItem sequence, and run BatchProcessor. 2) Implement BatchProcessor.cs with bounded channel, worker pool, progress reporting, and error capture; expose ProcessAsync returning BatchSummary. 3) Add tests in batch-csharp.Tests validating that all items are processed and failures don’t stop the batch. 4) Validate with dotnet build/test and document run instructions.

## Concrete Steps

- Run from repo root to build:
    dotnet build batch-csharp/BatchRunner.csproj
- Run batch with defaults (50k items, parallelism=CPU count):
    dotnet run --project batch-csharp/BatchRunner.csproj
- Override settings, e.g.:
    dotnet run --project batch-csharp/BatchRunner.csproj -- --count=200000 --parallel=8 --report-every=5000 --work-ms=2 --channel-capacity=50000
  (double-dash separates dotnet args from app args)
- Run tests:
    dotnet test batch-csharp.Tests/Batch-csharp.Tests.csproj

## Validation and Acceptance

Acceptance: `dotnet build` succeeds; `dotnet test` passes; running the app processes the requested number of items and logs progress every configured interval; CLI/env overrides are honored; batch does not halt on individual item failures (errors logged, rest continue).

## Idempotence and Recovery

Re-running the batch is safe; channel bounds prevent unbounded memory growth. Cancellation token support allows safe shutdown; restart resumes from the top of the sequence generator. Adjust channel capacity/parallelism to balance throughput vs. memory usage.

## Artifacts and Notes

Test run snapshot:
    dotnet test batch-csharp.Tests/Batch-csharp.Tests.csproj
    Passed! - Failed: 0, Passed: 2, Skipped: 0

Manual sample run (count=2000, parallel=4, work-ms=0, report-every=500):
    == Batch Runner (C#) ==
    Configured for 2,000 items, parallelism=4, reportEvery=500
    [2026-01-20T00:43:43.4175859Z] Processed 2,000 items (worker 3)
    [2026-01-20T00:43:43.4170323Z] Processed 1,000 items (worker 1)
    [2026-01-20T00:43:43.4169080Z] Processed 500 items (worker 2)
    [2026-01-20T00:43:43.4171902Z] Processed 1,500 items (worker 0)
    Completed 2,000 items in 0.03s

## Interfaces and Dependencies

Public types: WorkItem(Id:int, Payload:string); BatchProcessor.ProcessAsync(IEnumerable<WorkItem>, CancellationToken) -> BatchSummary(TotalProcessed:int, Elapsed:TimeSpan). Config: Settings parsed in Program.cs via flags/env. Dependencies: .NET 9.0 SDK/runtime, System.Threading.Channels, xUnit for tests.
