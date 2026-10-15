"""Audit history for CampusFlow Pro.

Events follow the format that storage.validate_events requires:
ticket_id, action, actor (non-empty strings) and a timezone-aware
ISO-8601 timestamp. An event is recorded only AFTER an operation has
succeeded; record_event validates everything first, so a bad call raises
ValueError and the events list is left untouched.
"""

from datetime import datetime, timezone

ACTIONS = ("CREATE", "ASSIGN", "START", "RESOLVE", "REOPEN", "ESCALATE")
VALID_STATUSES = ("open", "in_progress", "resolved")


def record_event(events, ticket_id, action, actor, timestamp,
                 before_status, after_status, details=None):
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("ticket_id is required.")

    if action not in ACTIONS:
        raise ValueError(f"Invalid action: {action}")

    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("actor is required.")

    if (not isinstance(timestamp, datetime)
            or timestamp.tzinfo is None
            or timestamp.utcoffset() is None):
        raise ValueError("timestamp must be timezone-aware.")

    if before_status is not None and before_status not in VALID_STATUSES:
        raise ValueError(f"Invalid before_status: {before_status}")

    if after_status not in VALID_STATUSES:
        raise ValueError(f"Invalid after_status: {after_status}")

    if details is None:
        details = {}
    if not isinstance(details, dict):
        raise ValueError("details must be a dictionary.")

    event = {
        "ticket_id": ticket_id,
        "action": action,
        "actor": actor,
        "timestamp": timestamp.astimezone(timezone.utc)
                              .replace(microsecond=0).isoformat(),
        "before_status": before_status,
        "after_status": after_status,
        "details": dict(details),
    }

    events.append(event)  # the only line that changes state
    return event


def get_ticket_history(events, ticket_id):
    """Return one ticket's events in the order they were recorded."""
    ticket_id = str(ticket_id).strip().upper()
    return [e for e in events if e.get("ticket_id") == ticket_id]


def format_event(event):
    before = event.get("before_status") or "-"
    after = event.get("after_status") or "-"
    return (
        f"{event['timestamp']} | {event['action']} | "
        f"{before} -> {after} | by {event['actor']}"
    )


def print_history(events, ticket_id):
    history = get_ticket_history(events, ticket_id)
    if not history:
        print("No history for that ticket.")
        return
    for event in history:
        print(format_event(event))