# Agent Instructions

## Project

Labeled corpus of LLM agent and RAG vulnerabilities. Each scenario
ships `vulnerable/`, `fixed/`, and `negative/` variants plus a
structured `finding.yaml`. The annotation is the deliverable. Code is
evidence.

Two artifact types: Python (schema, scenarios, sast, tests) and
TypeScript (`clients/ts/`, a stdio MCP client for scenario 04).

## Commands

    uv sync
    uv run pytest -q
    uv run ruff check .
    uv run ruff format --check .
    uv run pyright
    uvx semgrep --config sast/<rule>.yaml scenarios/<scenario>/

    cd clients/ts
    pnpm install
    pnpm run build
    pnpm run vulnerable   # or fixed, negative

## Rules

- One slice equals one commit. See PLAN.md for the slice breakdown.
- New scenario is five slices: vulnerable, fixed, negative, tests,
  annotations plus Semgrep. Do not skip the negative.
- The `negative/` variant must share the `vulnerable/` function
  verbatim. Safety comes from deployment context, not code.
- The `fixed/` variant should be a minimal diff. In scenario 04 it is
  a schema change (removing `user_id` from the tool contract), not a
  runtime check. Structural fixes are preferred where possible.
- Every `finding.yaml` must validate against `schema/finding.py`.
- `FlowSource.taint` is a `TaintLabel` enum, not a string.
- Do not add a Python dependency without checking 3.14 wheel support.
- Do not add a Node dependency without checking Node 20+ support.

## Boundaries

- Do not modify `schema/` without updating all existing `finding.yaml`
  files and re-running the corpus test.
- Do not create files with `Set-Content -Encoding utf8` on Windows.
  It writes a BOM that panics ruff. Use `New-Item` then paste in
  VS Code.
- Do not commit `node_modules/` or `dist/` under `clients/ts/`. They
  are gitignored; verify with `git status` after any pnpm command.
- Do not add a root `package.json`. The TS client is scoped to
  `clients/ts/` deliberately. Tools that want a root package should
  be invoked from `clients/ts/`.
- Do not claim scenario 04 reproduces CVE-2026-27124. That CVE is an
  OAuth consent flaw in FastMCP's OAuthProxy; scenario 04 is a
  tool-level confused deputy. The distinction is recorded in the
  scenario README and SECURITY.md.
