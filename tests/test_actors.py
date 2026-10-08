"""Tests for the canonical actor registry and its loader."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from schema.actors import ActorContext
from schema.finding import Finding
from schema.loaders import load_actors

FIXTURES = Path(__file__).parent / "fixtures"


def test_registry_loads() -> None:
    actors = load_actors()
    assert len(actors) >= 3
    assert "tenant_a_user" in actors
    assert isinstance(actors["tenant_a_user"], ActorContext)


def test_all_entries_are_typed() -> None:
    for name, actor in load_actors().items():
        assert isinstance(actor, ActorContext), name
        assert actor.tenant, f"{name}: missing tenant"


def test_missing_required_field_rejected() -> None:
    with pytest.raises(ValidationError):
        ActorContext.model_validate({"identity": "x"})


def test_fixture_actor_is_in_registry() -> None:
    """Every fixture finding must use a registered actor."""
    registered = {(a.identity, a.tenant, a.purpose) for a in load_actors().values()}

    for fixture in FIXTURES.glob("*.yaml"):
        data = yaml.safe_load(fixture.read_text(encoding="utf-8"))
        finding = Finding.model_validate(data)
        key = (
            finding.actor.identity,
            finding.actor.tenant,
            finding.actor.purpose,
        )
        assert key in registered, f"{fixture.name}: actor {key} not in canonical registry"
