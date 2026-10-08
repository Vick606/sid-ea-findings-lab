"""Validation tests for the finding annotation schema."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from schema.finding import Finding

FIXTURES = Path(__file__).parent / "fixtures"


def load_yaml(name: str) -> dict:
    return yaml.safe_load((FIXTURES / name).read_text(encoding="utf-8"))


def test_valid_sid_finding_loads() -> None:
    data = load_yaml("valid_sid.yaml")
    finding = Finding.model_validate(data)

    assert finding.class_.value == "SID"
    assert finding.severity.value == "HIGH"
    assert finding.flow.sink.kind.value == "llm_response"
    assert finding.trust_boundaries[0].violated is True


def test_valid_ea_finding_loads() -> None:
    data = load_yaml("valid_ea.yaml")
    finding = Finding.model_validate(data)

    assert finding.class_.value == "EA"
    assert finding.flow.sink.kind.value == "tool_call"
    assert finding.control.bypass is None


def test_missing_required_field_fails() -> None:
    data = load_yaml("valid_sid.yaml")
    del data["root_cause"]

    with pytest.raises(ValidationError):
        Finding.model_validate(data)


def test_invalid_severity_fails() -> None:
    data = load_yaml("valid_sid.yaml")
    data["severity"] = "SUPER_BAD"

    with pytest.raises(ValidationError):
        Finding.model_validate(data)


def test_unknown_field_is_rejected() -> None:
    data = load_yaml("valid_sid.yaml")
    data["typo_field"] = "oops"

    with pytest.raises(ValidationError):
        Finding.model_validate(data)


def test_id_class_mismatch_fails() -> None:
    data = load_yaml("valid_sid.yaml")
    data["id"] = "EA-2026-999"

    with pytest.raises(ValidationError, match="must start with SID-"):
        Finding.model_validate(data)
