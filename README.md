# sid-ea-findings-lab

A labeled corpus of LLM agent and RAG vulnerabilities where the primary
deliverable is a machine-readable *finding* — not a benchmark score.

Every scenario ships a vulnerable implementation, a fixed version, and a
hard negative that looks like a finding but isn't. The finding itself is
a structured YAML annotation that traces source-to-sink, states the
authorization context, identifies the missing control, and documents
residual risk. Runnable code is evidence that the annotation describes
something real.

## The gap

Existing LLM security benchmarks measure **behavior**:

- **PrivacyLens** (NeurIPS 2024) — vignettes and agent trajectories
  measuring privacy-norm adherence. Reports leak rates.
- **CIMemories** — contextual-integrity violations in persistent memory.
  Reports attribute-level violation rates.
- **POLAR-Bench** — privacy-utility trade-offs in agent conversations.
  Reports a diagnostic score.
- **AgentSecBench** — adversarial agent scenarios across instruction,
  retrieval, and capability integrity. Reports tier-graded robustness.

None of them ship a **triage-ready finding**. They answer *"did the agent
misbehave?"*. They don't answer *"what was the root cause, which control
was missing, who was the actor, what is the residual risk after the fix,
and how do I write a Semgrep rule that discriminates the vulnerable case
from the safe one?"*

This project ships that artifact.

## What this project contributes

1. **A finding schema** (`schema/finding.py`) that maps to the vocabulary
   a security reviewer actually uses: actor, trust boundary, source,
   propagation, sink, root cause, control, severity, residual risk.
2. **Four scenarios** covering Sensitive Information Disclosure (SID) and
   Excessive Agency (EA) across memory, retrieval, tool calling, and MCP.
3. **Hard negatives** — variants that look like findings but aren't —
   each with a written rationale (`WHY_NOT_A_FINDING.md`) stating the
   exact condition that would flip it into a real finding.
4. **Semgrep rules** that fire on the vulnerable variant and stay silent
   on the fixed and negative variants. Discrimination is tested in CI.
5. **Deterministic tests** using `FakeListChatModel` and fixed vectors —
   no API keys, no network, no variance.

## Repository layout

- `schema/` — Pydantic models for findings and actor contexts
- `scenarios/` — one directory per vulnerability, each with
  `vulnerable/`, `fixed/`, `negative/`, `finding.yaml`, `trace.md`,
  and `WHY_NOT_A_FINDING.md`
- `sast/` — Semgrep rules and the CI gate that verifies discrimination
- `calibration/` — labeled findings and non-findings with severity and
  confidence rationale
- `tests/` — schema and scenario tests
- `harness/` — runner that asserts variant behavior end-to-end

## Why traditional taint analysis doesn't transfer to LLM agents

Classical taint analysis assumes deterministic dataflow: a value is
copied from source to sink through identifiable operations on program
memory. Static analyzers can prove reachability because the propagation
rules are the language's own semantics.

LLM agents break this assumption. The propagation from a retrieved
document to a tool call happens *inside the model's reasoning*, expressed
in natural language. There is no memory address. There is no copy
instruction. The same input may or may not propagate depending on
sampling, prompt framing, or tool-selection heuristics. Taint tracking
across that boundary is semantic, not structural.

This project does not attempt to automate that analysis. It does
something a taint engine cannot: it **records the trace by hand**, for
each finding, in a form that a reviewer can read, audit, and disagree
with. The `flow` block in `finding.yaml` is the analyst's claim about how
untrusted data reached a privileged action. The tests then pin that claim
to deterministic behavior.

That is why the artifact is the annotation, not the scanner.

## Status

Stage 1 (Foundation & Schema) complete. Scenarios ship in Stages 2–5.

## Tooling

Python 3.14.7, `uv`, Pydantic 2.13+, LangChain, FastMCP 4, Semgrep
(taint mode), pytest, ruff, pyright. No Docker. No paid APIs.

## License

TBD.
