tickets = []

categories = ["Network", "Hardware", "Software", "Other"]
urgency_levels = ["low", "medium", "high"]


def list_tickets():
    print(" ALL TICKETS ")

    if not tickets:
        print("No tickets have been created yet.")
        return

    for ticket in tickets:
        print("-" * 35)
        for field, value in ticket.items():
            print(f"{field.replace('_', ' ').title()}: {value}")


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

    for field, value in ticket.items():
        print(f"{field.replace('_', ' ').title()}: {value}")
