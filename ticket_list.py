from datetime import datetime, timedelta, timezone

from sla import is_overdue
from ticket_creation import tickets

LOCAL_TZ = timezone(timedelta(hours=1))
TIME_FIELDS = ("creation_time", "sla_start", "deadline")


def to_local(iso_string):
    try:
        moment = datetime.fromisoformat(iso_string)
        return moment.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S") + " (WAT)"
    except (TypeError, ValueError):
        return str(iso_string)


def overdue_label(ticket, now=None):
    try:
        if ticket["status"] == "resolved":
            return "n/a (resolved)"
        return "YES" if is_overdue(ticket, now) else "No"
    except ValueError:
        return "unknown (invalid deadline)"


def print_ticket(ticket, now=None):
    for field, value in ticket.items():
        if field in TIME_FIELDS:
            value = to_local(value)
        print(f"{field.replace('_', ' ').title()}: {value}")
    print(f"Overdue: {overdue_label(ticket, now)}")


def list_tickets():
    print(" ALL TICKETS ")

    if not tickets:
        print("No tickets have been created yet.")
        return

    now = datetime.now(timezone.utc)
    for ticket in tickets:
        print("-" * 35)
        print_ticket(ticket, now)


def find_ticket(ticket_id):
    ticket_id = ticket_id.strip().upper()

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    return None


def view_ticket():
    print("\n===== VIEW TICKET =====")

    ticket_id = input("Enter the ticket ID: ")
    ticket = find_ticket(ticket_id)

    if ticket is None:
        print("Error: Ticket ID not found.")
        return

    print_ticket(ticket, datetime.now(timezone.utc))