
"""
CampusFlow ticket assignment and status management.
"""


VALID_STATUSES = ("open", "in_progress", "resolved")


def find_ticket(tickets, ticket_id):
    """Find a ticket by ID or raise an error if it doesn't exist."""

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise ValueError(f"Ticket {ticket_id} was not found.")


def assign_ticket(tickets, ticket_id, staff_name):
    """Assign an existing, unresolved ticket to a staff member."""

    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"] == "resolved":
        raise ValueError(
            "This ticket is resolved. Reopen it before making changes."
        )

    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty.")

    ticket["assigned_to"] = staff_name.strip()

    return ticket


def change_ticket_status(tickets, ticket_id, new_status):
    """
    Change a ticket's status.

    Normal progression:
        open -> in_progress -> resolved

    A resolved ticket must be explicitly reopened before further changes.
    """

    ticket = find_ticket(tickets, ticket_id)

    if not isinstance(new_status, str):
        raise ValueError("Status must be text.")

    new_status = new_status.strip().lower()

    if new_status not in VALID_STATUSES:
        raise ValueError(
            "Invalid status. Choose open, in_progress, or resolved."
        )

    current_status = ticket["status"]

    if current_status == "resolved":
        raise ValueError(
            "This ticket is resolved. Use reopen_ticket() first."
        )

    if current_status == "open" and new_status == "in_progress":
        if not ticket.get("assigned_to"):
            raise ValueError(
                "Assign the ticket to a staff member before starting work."
            )

        ticket["status"] = "in_progress"
        return ticket

    if current_status == "in_progress" and new_status == "resolved":
        ticket["status"] = "resolved"
        return ticket

    if current_status == new_status:
        raise ValueError(
            f"Ticket {ticket_id} is already {current_status}."
        )

    raise ValueError(
        f"Invalid status transition: {current_status} -> {new_status}."
    )


def reopen_ticket(tickets, ticket_id):
    """
    Explicitly reopen a resolved ticket.

    Reopening returns it to open status. It must be assigned again
    if a staff member is to start working on it.
    """

    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"] != "resolved":
        raise ValueError(
            "Only resolved tickets can be reopened."
        )

    ticket["status"] = "open"
    ticket["assigned_to"] = None

    return ticket

def get_unresolved_queue(tickets):
    """

    Return unresolved tickets in priority order.

    Priority order:
        critical -> high -> medium -> low

    Tickets with equal priority are sorted by numeric ticket ID.
    """

    priority_order = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "low": 4,
    }

    unresolved = [
        ticket
        for ticket in tickets
        if ticket["status"] != "resolved"
    ]

    def queue_sort_key(ticket):
        priority = priority_order.get(
            ticket["priority"].lower(),
            99,
        )

        ticket_id = ticket["id"]

        if (
            isinstance(ticket_id, str)

            and ticket_id.startswith("T")

            and ticket_id[1:].isdigit()
        ):
            numeric_id = int(ticket_id[1:])
        else:
            numeric_id = float("inf")

        return priority, numeric_id

    return sorted(unresolved, key=queue_sort_key)