import unittest
from ticket_create import create_ticket, tickets
from ticket_list import get_all_tickets, get_ticket


class TestTicketListing(unittest.TestCase):

    def setUp(self):
        tickets.clear()

        create_ticket(
            title="Internet failure",
            category="Network",
            urgency="high",
            affected_users=12
        )

        create_ticket(
            title="Broken keyboard",
            category="Hardware",
            urgency="low",
            affected_users=1
        )

    def test_list_all_tickets(self):
        result = get_all_tickets()

        self.assertEqual(len(result), 2)

    def test_list_returns_ticket_details(self):
        result = get_all_tickets()

        self.assertEqual(result[0]["title"], "Internet failure")
        self.assertEqual(result[1]["title"], "Broken keyboard")

    def test_find_existing_ticket(self):
        ticket = get_ticket("T001")

        self.assertIsNotNone(ticket)
        self.assertEqual(ticket["title"], "Internet failure")

    def test_find_nonexistent_ticket(self):
        ticket = get_ticket("T999")

        self.assertIsNone(ticket)


if __name__ == "__main__":
    unittest.main()