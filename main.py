import workflow
from ticket_creation import add, tickets
from ticket_list import list_tickets, view_ticket
from assign import assign_ticket
from report import print_report
from storage import save_tickets
from knowledge_lab import run_engineering_knowledge_lab


def change_status_menu():
    ticket_id = input("Enter the ticket ID: ").strip().upper()
    new_status = input("New status (open/in_progress/resolved): ")
    try:
        ticket = workflow.change_ticket_status(tickets, ticket_id, new_status)
        save_tickets(tickets)
        print(f"Ticket {ticket['id']} is now {ticket['status']}.")
    except ValueError as error:
        print(f"Error: {error}")


def reopen_menu():
    ticket_id = input("Enter the ticket ID: ").strip().upper()
    try:
        workflow.reopen_ticket(tickets, ticket_id)
        save_tickets(tickets)
        print(f"Ticket {ticket_id} reopened.")
    except ValueError as error:
        print(f"Error: {error}")


def queue_menu():
    queue = workflow.get_unresolved_queue(tickets)
    if not queue:
        print("No unresolved tickets.")
        return
    for ticket in queue:
        print(
            f"{ticket['id']} | {ticket['priority']} | "
            f"{ticket['status']} | {ticket['title']}"
        )


def main():
    while True:
        print("""
_______ CAMPUSFLOW _______
    1. Create Ticket
    2. List All Tickets
    3. View One Ticket
    4. Assign Ticket
    5. Print Report
    6. Change Ticket Status
    7. Reopen Ticket
    8. Unresolved Queue
    9. Engineering Knowledge Lab
    0. Exit""")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add()
        elif choice == "2":
            list_tickets()
        elif choice == "3":
            view_ticket()
        elif choice == "4":
            assign_ticket()
        elif choice == "5":
            print_report(tickets)
        elif choice == "6":
            change_status_menu()
        elif choice == "7":
            reopen_menu()
        elif choice == "8":
            queue_menu()
        elif choice == "9":
            run_engineering_knowledge_lab()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please select 0-9.")


if __name__ == "__main__":
    main()
