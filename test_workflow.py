
import unittest

from campusflow.workflow import (
    assign_ticket,
    change_ticket_status,
    find_ticket,
    get_unresolved_queue,
    reopen_ticket,
)


def make_ticket(
    ticket_id="T001",
    priority="low",
    status="open",
    assigned_to=None,
):
    """Create a ticket for testing workflow behaviour."""

    return {
        "id": ticket_id,
        "title": "Test ticket",
        "category": "Network",
        "urgency": "low",
        "affected_users": 1,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }


class TestTicketWorkflow(unittest.TestCase):

    def setUp(self):
        self.tickets = [
            make_ticket()
        ]

    def test_find_existing_ticket(self):
        ticket = find_ticket(self.tickets, "T001")

        self.assertEqual(ticket["id"], "T001")

    def test_unknown_ticket_is_rejected(self):
        with self.assertRaises(ValueError):
            find_ticket(self.tickets, "T999")

    def test_assign_ticket(self):
        ticket = assign_ticket(
            self.tickets,
            "T001",
            "Ada",
        )

        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_empty_staff_name_is_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets,
                "T001",
                "   ",
            )

    def test_unassigned_ticket_cannot_start(self):
        with self.assertRaises(ValueError):
            change_ticket_status(
                self.tickets,
                "T001",
                "in_progress",
            )

    def test_assigned_ticket_can_start(self):
        assign_ticket(self.tickets, "T001", "Ada")

        ticket = change_ticket_status(
            self.tickets,
            "T001",
            "in_progress",
        )

        self.assertEqual(ticket["status"], "in_progress")

    def test_ticket_can_be_resolved(self):
        assign_ticket(self.tickets, "T001", "Ada")

        change_ticket_status(
            self.tickets,
            "T001",
            "in_progress",
        )

        ticket = change_ticket_status(
            self.tickets,
            "T001",
            "resolved",
        )

        self.assertEqual(ticket["status"], "resolved")

    def test_resolved_ticket_must_be_reopened_explicitly(self):
        self.tickets[0]["status"] = "resolved"

        with self.assertRaises(ValueError):
            change_ticket_status(
                self.tickets,
                "T001",
                "open",
            )

    def test_reopening_resolved_ticket(self):
        self.tickets[0]["status"] = "resolved"
        self.tickets[0]["assigned_to"] = "Ada"

        ticket = reopen_ticket(self.tickets, "T001")

        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])

    def test_resolved_ticket_is_not_assigned_again_directly(self):
        self.tickets[0]["status"] = "resolved"

        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets,
                "T001",
                "Ada",
            )

    def test_queue_sorts_by_priority_then_id(self):
        tickets = [
            make_ticket("T004", "medium"),
            make_ticket("T003", "critical", "in_progress", "Ada"),
            make_ticket("T001", "high"),
            make_ticket("T002", "critical"),
            make_ticket("T005", "low", "resolved"),
        ]

        queue = get_unresolved_queue(tickets)

        ticket_ids = [
            ticket["id"]
            for ticket in queue
        ]

        self.assertEqual(
            ticket_ids,
            ["T002", "T003", "T001", "T004"],
        )

    def test_queue_with_no_tickets(self):
        self.assertEqual(get_unresolved_queue([]), [])


if __name__ == "__main__":
    unittest.main()