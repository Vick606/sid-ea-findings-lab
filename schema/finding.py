"""The Finding model — the primary deliverable of this corpus.

Every scenario ships one Finding. The Finding describes what was vulnerable,
who the actor was, which trust boundary was violated, the source-to-sink
path, the root cause, the control that was missing, and the residual risk
that survives the fix.
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from schema.actors import ActorContext
from schema.enums import Severity, SinkKind, SourceKind, VulnClass


class TrustBoundary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    from_actor: str
    to_actor: str
    expected_invariant: str
    violated: bool


class FlowSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: SourceKind
    location: str
    taint: str


class FlowStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step: str
    location: str
    note: str | None = None


class FlowSink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: SinkKind
    location: str
    action: str


class Flow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: FlowSource
    propagation: list[FlowStep]
    sink: FlowSink


class Control(BaseModel):
    model_config = ConfigDict(extra="forbid")

    present: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    bypass: str | None = None


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    test: str
    semgrep: str | None = None
    diff: str | None = None
    negative: str | None = None


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    class_: VulnClass = Field(alias="class")
    owasp_llm: str
    cwe: list[str] = Field(default_factory=list)
    title: str

    actor: ActorContext
    trust_boundaries: list[TrustBoundary]
    flow: Flow

    root_cause: str
    control: Control

    severity: Severity
    severity_rationale: str
    residual_risk: str

    evidence: Evidence

    @model_validator(mode="after")
    def id_matches_class(self) -> Finding:
        prefix = self.class_.value
        if not self.id.startswith(f"{prefix}-"):
            raise ValueError(
                f"id {self.id!r} must start with {prefix}- to match class {self.class_.value}"
            )
        return self
