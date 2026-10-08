# sid-ea-findings-lab

A labeled corpus of LLM agent and RAG vulnerabilities where the primary
deliverable is a machine-readable findings format. Runnable code serves
as evidence that the annotations describe something real.

## Status

Stage 1 — Foundation & Schema (in progress).

## What's here

- `scenarios/` — vulnerable / fixed / negative variants per vulnerability
- `harness/` — deterministic test runner and CI gate
- `sast/` — Semgrep rules that discriminate between variants
- `calibration/` — labeled findings and non-findings
- `docs/` — supporting notes

## License

TBD.
