# Security Policy

## Scope

This repository contains deliberately vulnerable code under
`scenarios/*/vulnerable/`. Those vulnerabilities are the corpus, not
defects. They exist to be found, annotated, and fixed.

Do not report vulnerabilities in the `vulnerable/` variants as security
issues. They are labeled, documented in `finding.yaml`, and paired with
a `fixed/` variant that closes them.

Two artifact types live here:

- **Python** under `schema/`, `scenarios/`, `sast/`, and `tests/`
- **TypeScript** under `clients/ts/` (a minimal MCP client using
  `@modelcontextprotocol/sdk`)

Both are in scope for the reporting rules below.

## What to report

Report issues with the repository itself:

- CI or test harness bypass that makes a variant pass when it should fail
- Semgrep rules that fire incorrectly on `fixed/` variants
- Schema validation gaps that allow malformed findings to pass
- MCP server defects outside the documented scenario, such as a
  vulnerable behavior in `fixed/` or `negative/` that a contrast test
  does not catch
- TypeScript client defects that do not reproduce the documented
  behavior (leak, schema rejection, not found)
- Dependencies with known CVEs, for either `uv` or `pnpm`
- Accidental inclusion of real secrets, credentials, or PII

## How to report

Do not open a public issue. Use GitHub's private vulnerability reporting:

https://github.com/Vick606/sid-ea-findings-lab/security/advisories/new

Include:

- Affected file or component
- Language and runtime (Python or TypeScript)
- Reproduction steps
- Impact
- Smallest safe test case

You will receive an acknowledgment within 72 hours. Fixes are
coordinated privately before public disclosure.

## Out of scope

- Any behavior of the `vulnerable/` variants. That is the corpus.
- Theoretical weaknesses in `fixed/` or `negative/` variants without a
  reproduction that passes the deterministic tests.
- The scenario-04 tool-level confused deputy being compared to
  CVE-2026-27124. That CVE is an OAuth consent-validation flaw in
  FastMCP's OAuthProxy, fixed in 3.2.0. Scenario 04 is a distinct
  tool-level pattern and does not claim to reproduce that CVE.
- Attacks requiring physical access to the runner.
- Findings that require disabling the pnpm lockfile or installing an
  unsupported Node or Python version.
