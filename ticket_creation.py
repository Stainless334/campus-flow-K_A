from storage import load_tickets, save_tickets

tickets = load_tickets()

categories = ["Network", "Hardware", "Software", "Other"]
urgency_levels = ["low", "medium", "high"]


def generate_ticket_id():
    numbers = [
        int(ticket["id"][1:])
        for ticket in tickets
        if ticket["id"].startswith("T") and ticket["id"][1:].isdigit()
    ]
    next_number = max(numbers, default=0) + 1
    return f"T{next_number:03d}"


def calculate_priority(urgency, affected_users):
    if urgency == "high" and affected_users >= 10:
        return "critical"
    elif urgency == "high" or affected_users >= 10:
        return "high"
    elif urgency == "medium" or affected_users >= 3:
        return "medium"
    else:
        return "low"


def add():
    while True:
        title = input("Enter the problem title: ").strip()
        if title:
            break
        print("The title cannot be blank.")

    while True:
        print("Categories: Network, Hardware, Software, Other")
        category = input("Enter the category: ").strip().title()
        if category in categories:
            break
        print("Please enter a valid category.")

    while True:
        print("Urgency levels: low, medium, high")
        urgency = input("Enter the urgency: ").strip().lower()
        if urgency in urgency_levels:
            break
        print("Please enter low, medium, or high.")

    while True:
        user_input = input("Enter the number of affected users: ").strip()
        try:
            affected_users = int(user_input)
            if affected_users > 0:
                break
            print("The number of affected users must be positive.")
        except ValueError:
            print("Enter a positive whole number.")

    priority = calculate_priority(urgency, affected_users)

    ticket = {
        "id": generate_ticket_id(),
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
    }

    tickets.append(ticket)
    save_tickets(tickets)

    print(f"\nTicket {ticket['id']} created successfully!")
    print(f"Priority: {ticket['priority']}")
    print(f"Status: {ticket['status']}")


if __name__ == "__main__":
    add()