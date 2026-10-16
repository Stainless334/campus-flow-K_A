import unittest
from unittest.mock import patch

import ticket_creation

EXISTING = {
    "id": "T001", "title": " Wi-Fi   Down ", "category": "Network",
    "status": "open", "priority": "low",
}


def run_add(tickets, inputs):
    """Run add() with fake input and fake storage; return the mocks."""
    with patch.object(ticket_creation, "tickets", tickets), \
         patch.object(ticket_creation, "save_tickets") as save_t, \
         patch.object(ticket_creation, "load_events", return_value=[]), \
         patch.object(ticket_creation, "save_events") as save_e, \
         patch("builtins.input", side_effect=inputs), \
         patch("builtins.print"):
        ticket_creation.add()
    return save_t, save_e


class DuplicateCliTests(unittest.TestCase):
    def test_cancelling_duplicate_creates_nothing(self):
        tickets = [dict(EXISTING)]
        save_t, save_e = run_add(
            tickets, ["wi-fi down", "network", "low", "1", "n"])
        self.assertEqual(len(tickets), 1)
        save_t.assert_not_called()
        save_e.assert_not_called()

    def test_confirming_duplicate_creates_ticket_and_create_event(self):
        tickets = [dict(EXISTING)]
        save_t, save_e = run_add(
            tickets, ["wi-fi down", "network", "low", "1", "y"])
        self.assertEqual(len(tickets), 2)
        saved_events = save_e.call_args[0][0]
        self.assertEqual([e["action"] for e in saved_events], ["CREATE"])

    def test_no_duplicate_means_no_prompt(self):
        tickets = []
        # Only four inputs; a duplicate prompt would run out of inputs.
        run_add(tickets, ["Printer jam", "hardware", "low", "1"])
        self.assertEqual(len(tickets), 1)


if __name__ == "__main__":
    unittest.main()