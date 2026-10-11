
from ticket_list import find_ticket
def assign_ticket():
    print("\n ASSIGN TICKET ")

    ticket_id = input("Enter the ticket ID: ")
    ticket = find_ticket(ticket_id)

    if ticket is None:
        print("Ticket ID not found.")
        return

    if ticket["status"] == "resolved":
        print("This ticket is closed. Reopen ticket before assigning.")
        return

    staff_name = input("Enter the staff member's name: ").strip()

    if not staff_name:
        print("Invalid Input: Staff member's name cannot be blank.")
        return

    ticket["assigned_to"] = staff_name

    print(f"Ticket {ticket['id']} assigned to {staff_name}.")

