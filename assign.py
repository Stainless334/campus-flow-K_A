from datetime import datetime, timezone

from ticket_list import find_ticket
from ticket_creation import tickets
from storage import save_tickets, load_events, save_events
from history import record_event


def assign_ticket():
    print("\n ASSIGN TICKET ")

    ticket_id = input("Enter the ticket ID: ").strip().upper()
    ticket = find_ticket(ticket_id)

    if ticket is None:
        print("Ticket ID not found.")
        return

    if ticket["status"] == "resolved":
        print("This ticket is closed. Reopen ticket before assigning.")
        return

    staff_name = input("Enter the staff member's name: ").strip().title()

    if not staff_name:
        print("Invalid Input: Staff member's name cannot be blank.")
        return

    previous_assignee = ticket.get("assigned_to")

    # Build and validate the event BEFORE changing the ticket.
    # If record_event raises, the ticket is untouched and nothing is saved.
    events = load_events()
    try:
        record_event(
            events,
            ticket["id"],
            "ASSIGN",
            "user",
            datetime.now(timezone.utc),
            ticket["status"],
            ticket["status"],
            {"assigned_to": staff_name, "previous_assignee": previous_assignee},
        )
    except ValueError as error:
        print(f"Error: {error}")
        return

    ticket["assigned_to"] = staff_name
    try:
        save_tickets(tickets)
        save_events(events)
    except ValueError as error:
        ticket["assigned_to"] = previous_assignee  # undo the in-memory change
        print(f"Error: could not save, assignment cancelled. ({error})")
        return

    print(f"Ticket {ticket['id']} assigned to {staff_name}.")