import unittest
from unittest.mock import patch
from ticket_create import tickets, add
from assign import assign_ticket


class TestTicketAssignment(unittest.TestCase):

    def setUp(self):
        tickets.clear()

        with patch("builtins.input", side_effect=[
            "Printer not working",
            "Hardware",
            "medium",
            "3"
        ]):
            with patch("builtins.print"):
                add()

    def test_assign_ticket_successfully(self):
        with patch("builtins.input", side_effect=["T001", "Chinedu"]):
            with patch("builtins.print"):
                assign_ticket()

        self.assertEqual(tickets[0]["assigned_to"], "Chinedu")

    def test_assign_nonexistent_ticket(self):
        with patch("builtins.input", return_value="T999"):
            with patch("builtins.print"):
                assign_ticket()

        self.assertIsNone(tickets[0]["assigned_to"])

    def test_blank_staff_name_is_rejected(self):
        with patch("builtins.input", side_effect=["T001", ""]):
            with patch("builtins.print"):
                assign_ticket()

        self.assertIsNone(tickets[0]["assigned_to"])

    def test_ticket_does_not_disappear_after_assignment(self):
        with patch("builtins.input", side_effect=["T001", "Chinedu"]):
            with patch("builtins.print"):
                assign_ticket()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]["id"], "T001")


if __name__ == "__main__":
    unittest.main()