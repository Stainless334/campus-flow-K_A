from ticket_creation import add
from ticket_list import list_tickets, view_ticket
from assign import assign_ticket
from report import print_report
from storage import load_tickets


def main():
    while True:
        print("""
_______ CAMPUSFLOW _______
    1. Create Ticket
    2. List All Tickets
    3. View One Ticket
    4. Assign Ticket
    5. Print Report
    6. Exit""")

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
            tickets = load_tickets()
            print_report(tickets)
        elif choice == "6":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please select 1-6.")


if __name__ == "__main__":
    main()