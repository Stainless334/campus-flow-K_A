"""
CampusFlow ticket reports and statistics.
"""


VALID_STATUSES = ("open", "in_progress", "resolved")

VALID_PRIORITIES = ("critical", "high", "medium", "low")


def generate_report(tickets):
    """
    Generate ticket totals and breakdowns by status and priority.

    The function returns a dictionary that can later be displayed
    in the command-line menu.
    """

    report = {
        "total": len(tickets),
        "by_status": {
            status: 0
            for status in VALID_STATUSES
        },
        "by_priority": {
            priority: 0
            for priority in VALID_PRIORITIES
        },
    }

    for ticket in tickets:
        status = ticket["status"].lower()
        priority = ticket["priority"].lower()

        if status in report["by_status"]:
            report["by_status"][status] += 1

        if priority in report["by_priority"]:
            report["by_priority"][priority] += 1

    return report


def print_report(tickets):
    """Print a readable summary of ticket statistics."""

    report = generate_report(tickets)

    print("\n========== CAMPUSFLOW TICKET REPORT ==========")

    print(f"\nTotal tickets: {report['total']}")

    print("\n--- Tickets by Status ---")

    for status, count in report["by_status"].items():
        print(f"{status.replace('_', ' ').title()}: {count}")

    print("\n--- Tickets by Priority ---")

    for priority, count in report["by_priority"].items():
        print(f"{priority.title()}: {count}")

    print("==============================================\n")