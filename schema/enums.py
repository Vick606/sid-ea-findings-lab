"""Controlled vocabularies for the finding schema."""

from enum import StrEnum


class VulnClass(StrEnum):
    SID = "SID"
    EA = "EA"


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Confidence(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SourceKind(StrEnum):
    USER_QUERY = "user_query"
    USER_INPUT = "user_input"
    RETRIEVED_DOC = "retrieved_doc"
    TOOL_OUTPUT = "tool_output"
    MEMORY = "memory"
    SYSTEM_PROMPT = "system_prompt"


class SinkKind(StrEnum):
    LLM_RESPONSE = "llm_response"
    TOOL_CALL = "tool_call"
    MEMORY_WRITE = "memory_write"
    EXTERNAL_API = "external_api"


class ProvenanceTag(StrEnum):
    SYSTEM_PROMPT = "system_prompt"
    USER_INPUT = "user_input"
    RETRIEVED_DOC = "retrieved_doc"
    TOOL_OUTPUT = "tool_output"


class TaintLabel(StrEnum):
    UNTRUSTED = "untrusted"
    SENSITIVE = "sensitive"
    TRUSTED = "trusted"
