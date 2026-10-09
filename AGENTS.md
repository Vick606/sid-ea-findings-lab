# Agent Instructions

## Project

Labeled corpus of LLM agent and RAG vulnerabilities. Each scenario
ships `vulnerable/`, `fixed/`, and `negative/` variants plus a
structured `finding.yaml`. The annotation is the deliverable. Code is
evidence.

## Commands

    uv sync
    uv run pytest -q
    uv run ruff check .
    uv run ruff format --check .
    uv run pyright
    uvx semgrep --config sast/<rule>.yaml scenarios/<scenario>/

## Rules

- One slice equals one commit. See PLAN.md for the slice breakdown.
- New scenario is five slices: vulnerable, fixed, negative, tests,
  annotations plus Semgrep. Do not skip the negative.
- The `negative/` variant must share the `vulnerable/` function
  verbatim. Safety comes from deployment context, not code.
- Every `finding.yaml` must validate against `schema/finding.py`.
- `FlowSource.taint` is a `TaintLabel` enum, not a string.
- Do not add a dependency without checking Python 3.14 wheel support.

## Boundaries

- Do not modify `schema/` without updating all existing `finding.yaml`
  files and re-running the corpus test.
- Do not create files with `Set-Content -Encoding utf8` on Windows.
  It writes a BOM that panics ruff. Use `New-Item` then paste in
  VS Code.
