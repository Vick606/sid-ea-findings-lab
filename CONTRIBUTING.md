# Contributing

## Adding a scenario

Each scenario is five slices, one commit each:

1. Vulnerable variant: `scenarios/<name>/vulnerable/app.py`
2. Fixed variant: one-line diff from vulnerable
3. Hard negative: shares the vulnerable function verbatim, safe by
   deployment context
4. Deterministic tests: four tests, including a contrast test that
   runs the negative against the vulnerable store
5. Annotations: `finding.yaml`, `trace.md`, `WHY_NOT_A_FINDING.md`,
   and a Semgrep rule in `sast/`

## Required artifacts

    scenarios/<name>/
    ├── common.py
    ├── vulnerable/app.py
    ├── fixed/app.py
    ├── negative/app.py
    ├── tests/test_<name>.py
    ├── finding.yaml
    ├── trace.md
    ├── WHY_NOT_A_FINDING.md
    └── README.md

## Verification

Before committing:

    uv run pytest -q
    uv run ruff check .
    uv run ruff format --check .
    uv run pyright
    uvx semgrep --config sast/ scenarios/

The Semgrep rule must fire on `vulnerable/` and `negative/`, and stay
silent on `fixed/`. Document the negative as a false positive in the
rule metadata.

## Dependencies

The corpus runs on the Python standard library plus `numpy`, `pyyaml`,
and `pydantic`. Do not add a dependency without a strong reason.
