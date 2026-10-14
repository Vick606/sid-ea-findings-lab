"""Deterministic tests for scenario 03.

The vulnerable, fixed, and negative variants share agent_turn() by
design. The tests pin the security-relevant behavior of each: what
sends, what does not, and why the negative is safe despite sharing the
vulnerable function.

The fourth test is the contrast test. It runs the negative variant's
verbatim agent_turn() with a permissive tool and asserts the send
occurs. This proves the negative is safe because of tool configuration,
not code.
"""

from scenarios.agency_retrieved_doc.common import (
    ATTACKER_ADDRESS,
    BENIGN_DOC,
    MALICIOUS_DOC,
    PARTNER_ADDRESS,
    USER_MESSAGE_SUMMARIZE,
    EmailTool,
)
from scenarios.agency_retrieved_doc.fixed import app as fixed_app
from scenarios.agency_retrieved_doc.negative import app as negative_app
from scenarios.agency_retrieved_doc.vulnerable import app as vulnerable_app

DOCS = [BENIGN_DOC, MALICIOUS_DOC]


def _sent_to(calls: list, address: str) -> bool:
    return any(call.args["to"] == address for call in calls)


def test_vulnerable_sends_to_attacker() -> None:
    """Vulnerable agent_turn() with a permissive tool sends to the attacker."""
    email = EmailTool()
    calls = vulnerable_app.agent_turn(USER_MESSAGE_SUMMARIZE, DOCS, email)
    assert _sent_to(calls, ATTACKER_ADDRESS), (
        "expected the vulnerable variant to send to the attacker address"
    )


def test_fixed_does_not_send_to_attacker() -> None:
    """Fixed agent_turn() drops retrieved-doc instructions before the tool."""
    email = EmailTool()
    calls = fixed_app.agent_turn(USER_MESSAGE_SUMMARIZE, DOCS, email)
    assert not _sent_to(calls, ATTACKER_ADDRESS), "fixed variant sent to the attacker address"


def test_negative_does_not_send_to_attacker() -> None:
    """Negative agent_turn() with an allowlisted tool cannot reach the attacker."""
    email = EmailTool(allowed_recipients={PARTNER_ADDRESS})
    calls = negative_app.agent_turn(USER_MESSAGE_SUMMARIZE, DOCS, email)
    assert not _sent_to(calls, ATTACKER_ADDRESS), "negative variant sent to the attacker address"


def test_negative_function_sends_against_permissive_tool() -> None:
    """Contrast test: the negative's agent_turn() is code-identical to
    the vulnerable one.

    Run it with a permissive tool and the send occurs. This proves the
    negative is not a finding because of tool configuration, not code.
    """
    email = EmailTool()
    calls = negative_app.agent_turn(USER_MESSAGE_SUMMARIZE, DOCS, email)
    assert _sent_to(calls, ATTACKER_ADDRESS), (
        "expected the negative's agent_turn() to send against a permissive "
        "tool; if it does not, the negative is safe for the wrong reason"
    )
