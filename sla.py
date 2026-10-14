from datetime import datetime, timedelta, timezone


sla_duration = {
    "critical": timedelta(minutes=60),
    "high": timedelta(minutes=240),
    "medium": timedelta(minutes=1440),
    "low": timedelta(minutes=2880),
}


def calculate_due_at(priority, cycle_start):

    if priority not in sla_duration:
        raise ValueError(f"Invalid priority: {priority}")

    if cycle_start.tzinfo is None or cycle_start.utcoffset() is None:
        raise ValueError("cycle_start must be timezone-aware.")

    duration = sla_duration[priority]

    due_at = cycle_start + duration

    return due_at


def is_overdue(ticket, now=None):

    if ticket.get("status") in ("resolved", "closed"):
        return False

    due_at_value = ticket.get("due_at")

    if not due_at_value:
        raise ValueError("Ticket is missing its due_at deadline.")

    try:
        due_at = datetime.fromisoformat(due_at_value)
    except (TypeError, ValueError) as error:
        raise ValueError("Ticket has an invalid due_at deadline.") from error

    if due_at.tzinfo is None or due_at.utcoffset() is None:
        raise ValueError("Ticket deadline must be timezone-aware.")

    if now is None:
        now = datetime.now(timezone.utc)

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware.")

    return now > due_at