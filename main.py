from datetime import datetime, timezone

import workflow
from ticket_creation import add, tickets
from ticket_list import list_tickets, view_ticket
from assign import assign_ticket
from report import print_report
from storage import save_tickets, load_events, save_events
from sla import escalate_overdue, is_overdue
from history import record_event, print_history
from knowledge_lab import run_engineering_knowledge_lab
from queues import get_sla_attention_queue, calculate_metrics


STATUS_TO_EVENT = {"in_progress": "START", "resolved": "RESOLVE"}


def find_ticket(ticket_id):
    for ticket in tickets:
        if ticket.get("id") == ticket_id:
            return ticket
    return None


def change_status_menu():
    ticket_id = input("Enter the ticket ID: ").strip().upper()
    new_status = input("New status (open/in_progress/resolved): ").strip()

    existing = find_ticket(ticket_id)
    before = existing["status"] if existing else None

    try:
        ticket = workflow.change_ticket_status(tickets, ticket_id, new_status)
    except ValueError as error:
        print(f"Error: {error}")
        return  # rejected: no event, nothing saved

    event_type = STATUS_TO_EVENT.get(ticket["status"])
    if event_type:
        events = load_events()
        record_event(
            events,
            ticket["id"],
            event_type,
            "user",
            datetime.now(timezone.utc),
            before,
            ticket["status"],
        )
        save_events(events)

    save_tickets(tickets)
    print(f"Ticket {ticket['id']} is now {ticket['status']}.")


def reopen_menu():
    ticket_id = input("Enter the ticket ID: ").strip().upper()

    existing = find_ticket(ticket_id)
    before = existing["status"] if existing else None

    try:
        workflow.reopen_ticket(tickets, ticket_id)
    except ValueError as error:
        print(f"Error: {error}")
        return  # rejected: no event, nothing saved

    events = load_events()
    record_event(
        events,
        ticket_id,
        "REOPEN",
        "user",
        datetime.now(timezone.utc),
        before,
        "open",
    )
    save_events(events)
    save_tickets(tickets)
    print(f"Ticket {ticket_id} reopened.")


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


def escalate_menu():
    events = load_events()
    now = datetime.now(timezone.utc)  # the real clock is read only here

    try:
        new_events = escalate_overdue(tickets, events, now, "system")
        overdue_total = sum(1 for t in tickets if is_overdue(t, now))
    except ValueError as error:
        print(f"Escalation aborted, nothing was changed: {error}")
        return

    if new_events:
        save_events(events)
        for event in new_events:
            print(f"Escalated {event['ticket_id']}")

    already = overdue_total - len(new_events)
    print(f"Newly escalated: {len(new_events)} | Already escalated: {already}")


def history_menu():
    ticket_id = input("Enter the ticket ID: ").strip().upper()
    if not ticket_id:
        print("Error: ticket ID is required.")
        return
    events = load_events()
    print_history(events, ticket_id)


def sla_queue_menu():
    now = datetime.now(timezone.utc)
    try:
        queue = get_sla_attention_queue(tickets, now)
    except ValueError as error:
        print(f"Error: {error}")
        return
    if not queue:
        print("No unresolved tickets.")
        return
    for ticket in queue:
        flag = "OVERDUE" if is_overdue(ticket, now) else "on time"
        print(
            f"{ticket['id']} | {flag} | due {ticket['deadline']} | "
            f"{ticket['priority']} | {ticket['title']}"
        )


def metrics_menu():
    now = datetime.now(timezone.utc)
    try:
        metrics = calculate_metrics(tickets, load_events(), now)
    except ValueError as error:
        print(f"Error: {error}")
        return
    for name, value in metrics.items():
        print(f"{name}: {value}")


def main():
    while True:
        print("""
_______ CAMPUSFLOW PRO _______
    1. Create Ticket
    2. List All Tickets
    3. View One Ticket
    4. Assign Ticket
    5. Print Report
    6. Change Ticket Status
    7. Reopen Ticket
    8. Unresolved Queue
    9. Escalate Overdue Tickets
    10. View Ticket History
    11. Engineering Knowledge Lab
    12. SLA Attention Queue
    13. Metrics
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
            escalate_menu()
        elif choice == "10":
            history_menu()
        elif choice == "11":
            run_engineering_knowledge_lab()
        elif choice == "12":
            sla_queue_menu()
        elif choice == "13":
            metrics_menu()
        elif choice == "0":
            print("THANKS FOR USING CAMPUSFLOW PRO-VERSION 👍👍👍")
            break
        else:
            print("Invalid choice. Please select 0-13.")


if __name__ == "__main__":
    main()