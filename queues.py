"""Duplicate detection, SLA attention queue and metrics (Engineer B)."""

from datetime import datetime

from sla import is_overdue


def normalize_text(value):
    """Trim, case-fold and collapse whitespace: ' Wi-Fi   Down ' -> 'wi-fi down'."""
    return " ".join(str(value).casefold().split())


def detect_duplicates(category, title, tickets):
    """Return unresolved tickets with the same normalized title and category."""
    wanted_title = normalize_text(title)
    wanted_category = normalize_text(category)
    return [
        t for t in tickets
        if t.get("status") != "resolved"
        and normalize_text(t.get("title", "")) == wanted_title
        and normalize_text(t.get("category", "")) == wanted_category
    ]


def confirm_duplicates(category, title, tickets, input_fn=input, print_fn=print):
    """Warn about duplicates. Return True if creation may continue."""
    matches = detect_duplicates(category, title, tickets)
    if not matches:
        return True

    print_fn("Warning: similar unresolved ticket(s) already exist:")
    for t in matches:
        print_fn(f"  {t['id']} | {t['status']} | {t['title']}")

    while True:
        answer = input_fn("Create this ticket anyway? (y/n): ").strip().lower()
        if answer == "y":
            return True
        if answer == "n":
            return False
        print_fn("Please enter y or n.")


def get_sla_attention_queue(tickets, now):
    """Unresolved tickets: overdue first, then earliest deadline, then ID."""
    def sort_key(ticket):
        overdue = is_overdue(ticket, now)
        deadline = datetime.fromisoformat(ticket["deadline"])
        return (0 if overdue else 1, deadline, ticket["id"])

    unresolved = [t for t in tickets if t.get("status") != "resolved"]
    return sorted(unresolved, key=sort_key)


def calculate_metrics(tickets, events, now):
    """Each ticket is counted once in exactly one status bucket."""
    metrics = {
        "total": len(tickets),
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
        "overdue": 0,
        "escalation_events": sum(
            1 for e in events if e.get("action") == "ESCALATE"
        ),
    }
    for ticket in tickets:
        status = ticket.get("status")
        if status in ("open", "in_progress", "resolved"):
            metrics[status] += 1
        if is_overdue(ticket, now):
            metrics["overdue"] += 1
    return metrics