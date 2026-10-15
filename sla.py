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

    return cycle_start + sla_duration[priority]


def is_overdue(ticket, now=None):
    if ticket.get("status") in ("resolved", "closed"):
        return False

    deadline_value = ticket.get("deadline")
    if not deadline_value:
        raise ValueError("Ticket is missing its deadline.")

    try:
        deadline = datetime.fromisoformat(deadline_value)
    except (TypeError, ValueError) as error:
        raise ValueError("Ticket has an invalid deadline.") from error

    if deadline.tzinfo is None or deadline.utcoffset() is None:
        raise ValueError("Ticket deadline must be timezone-aware.")

    if now is None:
        now = datetime.now(timezone.utc).replace(microsecond=0)

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware.")

    return now > deadline


def escalate_overdue(tickets, events, now, actor):
    new_events = []

    for ticket in tickets:
        if not is_overdue(ticket, now):
            continue

        cycle_start = ticket.get("sla_start")
        if not cycle_start:
            raise ValueError(f"Ticket {ticket.get('id')} is missing sla_start.")

       

    events.extend(new_events)  
    return new_events