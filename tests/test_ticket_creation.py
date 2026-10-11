import unittest
from unittest.mock import patch

from ticket_create import tickets, add


class TestTicketCreation(unittest.TestCase):

    def setUp(self):
        tickets.clear()
    
    def test_create_ticket(self):
        answers = [
            
            "Faulty laptop",
            "Hardware",
            "high",
            "2",
        ]

        with patch("builtins.input", side_effect=answers):
            with patch("builtins.print"):
                add()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]["id"], "T001")
        self.assertEqual(tickets[0]["title"], "Faulty laptop")
        self.assertEqual(tickets[0]["category"], "Hardware")
        self.assertEqual(tickets[0]["urgency"], "high")
        self.assertEqual(tickets[0]["affected_users"], 2)
        self.assertEqual(tickets[0]["priority"], "high")
        self.assertEqual(tickets[0]["status"], "open")
        self.assertIsNone(tickets[0]["assigned_to"])


if __name__ == "__main__":
    unittest.main()