# Security Policy

## Scope

This repository contains deliberately vulnerable code under
`scenarios/*/vulnerable/`. Those vulnerabilities are the corpus, not
defects. They exist to be found, annotated, and fixed.

Do not report vulnerabilities in the `vulnerable/` variants as security
issues. They are labeled, documented in `finding.yaml`, and paired with
a `fixed/` variant that closes them.

## What to report

Report issues with the repository itself:

- CI or test harness bypass that makes a variant pass when it should fail
- Semgrep rules that fire incorrectly on `fixed/` variants
- Schema validation gaps that allow malformed findings to pass
- Dependencies with known CVEs
- Accidental inclusion of real secrets, credentials, or PII

## How to report

Do not open a public issue. Use GitHub's private vulnerability reporting:

https://github.com/Vick606/sid-ea-findings-lab/security/advisories/new

Include:

- Affected file or component
- Reproduction steps
- Impact
- Smallest safe test case

You will receive an acknowledgment within 72 hours. Fixes are
coordinated privately before public disclosure.

## Out of scope

- Any behavior of the `vulnerable/` variants. That is the corpus.
- Theoretical weaknesses in `fixed/` variants without a reproduction
  that passes the deterministic tests.
- Attacks requiring physical access to the runner.
