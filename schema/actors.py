"""Authorization context in which an agent acts.

A finding is only meaningful relative to a specific actor. Two runs of the
same code with different actors may differ in whether they disclose or act
impermissibly. Every Finding in this corpus is scoped to an ActorContext.
"""

from pydantic import BaseModel, ConfigDict, Field


class ActorContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity: str
    tenant: str
    scopes: list[str] = Field(default_factory=list)
    purpose: str
    permitted_recipients: list[str] = Field(default_factory=list)
    document_acl: str
