"""Structured finding annotations for LLM agent/RAG vulnerabilities."""

from schema.actors import ActorContext
from schema.enums import (
    Confidence,
    ProvenanceTag,
    Severity,
    SinkKind,
    SourceKind,
    TaintLabel,
    VulnClass,
)
from schema.finding import (
    Control,
    Evidence,
    Finding,
    Flow,
    FlowSink,
    FlowSource,
    FlowStep,
    TrustBoundary,
)
from schema.loaders import load_actors

__all__ = [
    "ActorContext",
    "Confidence",
    "Control",
    "Evidence",
    "Finding",
    "Flow",
    "FlowSink",
    "FlowSource",
    "FlowStep",
    "ProvenanceTag",
    "Severity",
    "SinkKind",
    "SourceKind",
    "TaintLabel",
    "TrustBoundary",
    "VulnClass",
    "load_actors",
]
