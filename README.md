<div align="center">

# sid-ea-findings-lab

**A labeled corpus of LLM agent and RAG vulnerabilities where the deliverable is a structured finding, not a benchmark score.**

Every scenario ships a vulnerable implementation, a fixed version, and a hard negative that looks like a finding but isn't — traced, annotated, tested, and explained.

[![License: AGPL v3 + CC BY-NC-SA 4.0](https://img.shields.io/badge/License-AGPL_v3_%2B_CC_BY--NC--SA_4.0-blue.svg)](LICENSING.md)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-16_passing-brightgreen.svg)](#validation)
[![OWASP LLM](https://img.shields.io/badge/OWASP_LLM-LLM02_%2F_LLM06-purple)](https://genai.owasp.org/llm-top-10/)
[![Semgrep](https://img.shields.io/badge/semgrep-taint_mode-red)](sast/)

</div>

---

## The gap

Existing LLM security benchmarks — [PrivacyLens](https://arxiv.org/abs/2406.18918), CIMemories, POLAR-Bench, AgentSecBench — measure **behavior** and report leak rates or robustness scores.

None of them ship a **triage-ready finding**. They answer *"did the agent misbehave?"*. They don't answer: what was the root cause? Which control was missing? Who was the actor? What is the residual risk? How do I write a SAST rule that discriminates the vulnerable case from the safe one — and what do I do when it fires on a non-finding?

This repository ships that artifact.

## The artifact

Each scenario produces a `finding.yaml` that a triage engineer, SAST pipeline, or reviewer can consume:

```yaml
id: SID-2026-001
class: SID
owasp_llm: "LLM02:2025"
cwe: [CWE-200, CWE-639]
title: Cross-tenant document disclosure via re-ranker ACL bypass

actor:
  identity: tenant_user
  tenant: tenant_a
  scopes: [rag:read]
  purpose: answer_internal_query
  document_acl: tenant_a_only

trust_boundaries:
  - name: tenant_isolation
    expected_invariant: "no tenant_b chunks returned to tenant_a"
    violated: true

flow:
  source: { kind: user_query,   location: "vulnerable/app.py:24", taint: untrusted }
  sink:   { kind: llm_response, location: "vulnerable/app.py:26", action: disclose_chunk_text }

root_cause: |
  The tenant predicate is applied at initial vector search and assumed
  to hold downstream. Unfiltered neighbor expansion re-introduces
  cross-tenant documents that nothing re-filters.

control:
  present: [initial_search_tenant_filter]
  missing: [post_rerank_acl_check]
  bypass:  unfiltered_neighbor_expansion

severity: HIGH
residual_risk: |
  Shared vector index remains queryable outside the agent path.
  Embedding inversion is out of scope and tracked separately.
```

Full schema: [`schema/finding.py`](schema/finding.py). Trace: [`scenarios/tenant_leak/trace.md`](scenarios/tenant_leak/trace.md).

## What ships per scenario

Three variants with **minimal security-relevant differences**:

| Variant | Purpose |
|---|---|
| `vulnerable/` | The finding. Reproducible leak or impermissible action. |
| `fixed/` | The one-line change that closes the finding. |
| `negative/` | **Hard negative** — shares the vulnerable code shape, safe by deployment context. |

Plus `finding.yaml`, `trace.md`, `WHY_NOT_A_FINDING.md`, and a scenario README.

| # | Scenario | Class | OWASP | Status |
|---|---|---|---|---|
| 01 | [Cross-tenant RAG leak](scenarios/tenant_leak/) | SID | LLM02 | ✅ Shipped |
| 02 | Cross-user memory bleed | SID | LLM02 | Planned |
| 03 | Retrieved-doc → outbound tool call | EA | LLM06 | Planned |
| 04 | MCP confused deputy | EA | LLM06 | Planned |

## Why the hard negatives matter

A naïve non-finding differs from the vulnerable case in an obvious way. That's not a test of judgment. The negatives here share the vulnerable code **verbatim** and are safe only because of a deployment assumption.

In scenario 01, the negative's `retrieve()` is byte-for-byte identical to the vulnerable variant's. A code-pattern matcher cannot tell them apart. That is documented, tested, and the reason the deterministic tests exist.

See [`WHY_NOT_A_FINDING.md`](scenarios/tenant_leak/WHY_NOT_A_FINDING.md).

## Why traditional taint analysis doesn't transfer

Classical taint analysis assumes deterministic dataflow through program memory. LLM agents propagate data *inside the model's reasoning* — no memory address, no copy instruction, sampling-dependent. Taint across that boundary is semantic, not structural.

This project doesn't automate that analysis. It **records the trace by hand** for each finding, in a form a reviewer can audit and disagree with. The `flow` block is the analyst's claim; the deterministic tests pin it to behavior.

## SAST integration

Semgrep rules in [`sast/`](sast/) run in taint mode and are validated against all three variants.

| Rule | Fires on vulnerable | Fires on fixed | Fires on negative |
|---|---|---|---|
| [`sid_rag_no_post_rerank_acl.yaml`](sast/sid_rag_no_post_rerank_acl.yaml) | ✅ | ❌ | ✅ (documented FP) |

The rule catches **code shape**; the tests catch **deployment context**. That trade-off is exactly what a GenAI security evaluation engineer negotiates.

## Install and test

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest -v
uv run python -m scenarios.tenant_leak.vulnerable.app   # reproduces the leak
uv run python -m scenarios.tenant_leak.fixed.app        # no leak
uvx semgrep --config sast/ scenarios/
```

No Docker. No model downloads. No API keys. Tests use `FakeListChatModel` and fixed vectors.

## Validation

Every commit runs:

```bash
uv run pytest -q              # 16 passing
uv run ruff check .
uv run ruff format --check .
uv run pyright
uvx semgrep --config sast/ scenarios/
```

[`tests/test_scenario_findings.py`](tests/test_scenario_findings.py) walks `scenarios/*/finding.yaml` and asserts each parses against the schema, declares a trust boundary, marks at least one violated, and names the missing control.

## Limitations

This is a **small, hand-built corpus**, not a benchmark.

**Good at:** structured findings consumable by triage tools; hard negatives that test judgment; auditable traces; reproducible with zero network; Semgrep rules that discriminate by code shape.

**Weak at:** scale (four scenarios, not four hundred); automation (traces are hand-written); coverage (no encoded attacks, multi-turn drift, or chained tool calls); multi-agent scenarios.

**Known trade-off:** the Semgrep rule fires on the hard negative. Not a bug — SAST sees code, not deployment. A rule that stayed silent would have to encode the deployment assumption, becoming brittle in the other direction.

> ⚠️ **Contains deliberately vulnerable code.** Do not deploy the `vulnerable/` variants.

## Repository layout

```
sid-ea-findings-lab/
├── schema/               # Pydantic models: finding, actor, enums
├── actors.yaml           # Canonical actor contexts
├── scenarios/
│   └── tenant_leak/
│       ├── vulnerable/   # the finding
│       ├── fixed/        # one-line fix
│       ├── negative/     # hard negative
│       ├── tests/
│       ├── finding.yaml
│       ├── trace.md
│       ├── WHY_NOT_A_FINDING.md
│       └── README.md
├── sast/                 # Semgrep rules
├── tests/                # schema + corpus validation
├── LICENSING.md
├── LICENSE               # AGPL-3.0-or-later (code)
└── LICENSE-CORPUS        # CC BY-NC-SA 4.0 (findings, docs)
```

## License

Split license. See [LICENSING.md](LICENSING.md).

| Artifact | License |
|---|---|
| Code (`*.py`, `sast/*.yaml`) | AGPL-3.0-or-later |
| Findings corpus, traces, docs | CC BY-NC-SA 4.0 |

The code is a teaching aid that should stay open. The annotated vulnerable patterns should not be packaged commercially without the defensive context. No commercial license is offered for the corpus.

## Status

Stage 2 complete — scenario 01 ships end to end. Stages 3–5 add three more scenarios. Stage 6 adds a calibration set and CI.

---

<div align="center">

**Built by [Victor](https://github.com/Vick606) — focused on GenAI security evaluation.**

</div>
