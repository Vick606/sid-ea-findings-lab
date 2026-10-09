"""Validate every scenario's finding.yaml against the schema.

The finding annotation is the primary deliverable of this corpus. This
test walks scenarios/*/finding.yaml, validates each against the Finding
model, and asserts the corpus is non-empty.
"""

from pathlib import Path

import pytest
import yaml

from schema.finding import Finding

SCENARIOS_DIR = Path(__file__).resolve().parent.parent / "scenarios"


def find_scenario_findings() -> list[Path]:
    return sorted(SCENARIOS_DIR.glob("*/finding.yaml"))


def test_at_least_one_scenario_finding_exists() -> None:
    findings = find_scenario_findings()
    assert findings, (
        f"no finding.yaml found under {SCENARIOS_DIR}; scenarios must ship a structured finding"
    )


@pytest.mark.parametrize(
    "path",
    find_scenario_findings(),
    ids=lambda p: p.parent.name,
)
def test_scenario_finding_loads(path: Path) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    finding = Finding.model_validate(data)

    assert finding.trust_boundaries, "finding must declare a trust boundary"
    assert any(b.violated for b in finding.trust_boundaries), (
        "at least one trust boundary must be marked violated"
    )
    assert finding.control.missing, "finding must name the missing control"
