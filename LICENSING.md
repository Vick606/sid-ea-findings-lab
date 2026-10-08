# Licensing

This repository contains two artifact types with different dual-use
profiles. They are licensed separately.

## Code

All Python source files (`*.py`) and Semgrep rules (`sast/*.yaml`) are
licensed under **AGPL-3.0-or-later**. See [LICENSE](LICENSE).

## Findings corpus and documentation

All annotations, traces, and narrative documents — including
`finding.yaml`, `trace.md`, `WHY_NOT_A_FINDING.md`, `actors.yaml`, and
scenario READMEs — are licensed under **CC BY-NC-SA 4.0**. See
[LICENSE-CORPUS](LICENSE-CORPUS).

## Rationale

The code is deliberately vulnerable. The AGPL ensures derivatives that
deploy it remain open, so the defensive context travels with the
vulnerable pattern.

The findings corpus documents those vulnerabilities, their root causes,
and their fixes. The NonCommercial clause prevents the annotated
vulnerable patterns and attack demonstrations from being packaged into
commercial offensive tooling without that defensive context.

The split matters because the two artifacts have different risk
profiles. The code is a teaching aid; the corpus is an analysis. A
fork that ships the vulnerable code under AGPL must keep the source
open. A fork that ships the corpus commercially must negotiate a
separate license, which creates a checkpoint for reviewing intent.

## Educational use

This repository is for security research and education only. **Do not
deploy the vulnerable variants.** They exist to be found, annotated,
and fixed. They are not production code and were never intended to be.

## Commercial licensing

No commercial license is offered for the findings corpus. If you have a
use case that the NonCommercial clause blocks, open an issue describing
the intended use. The answer will usually be a discussion about the
defensive context, not a sale.
