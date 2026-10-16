import unittest
from unittest.mock import patch

import assign


def make_ticket(status="open"):
    return {"id": "T001", "status": status, "assigned_to": None}


def run_assign(tickets, inputs):
    def fake_find(ticket_id):
        return next((t for t in tickets if t["id"] == ticket_id), None)

    with patch.object(assign, "tickets", tickets), \
         patch.object(assign, "find_ticket", side_effect=fake_find), \
         patch.object(assign, "save_tickets") as save_t, \
         patch.object(assign, "load_events", return_value=[]), \
         patch.object(assign, "save_events") as save_e, \
         patch("builtins.input", side_effect=inputs), \
         patch("builtins.print"):
        assign.assign_ticket()
    return save_t, save_e


class AssignEventTests(unittest.TestCase):
    def test_successful_assignment_records_one_assign_event(self):
        tickets = [make_ticket()]
        save_t, save_e = run_assign(tickets, ["t001", "IKWUJE"])
        self.assertEqual(tickets[0]["assigned_to"], "IKWUJE")
        saved = save_e.call_args[0][0]
        self.assertEqual([e["action"] for e in saved], ["ASSIGN"])
        self.assertEqual(saved[0]["details"]["assigned_to"], "IKWUJE")

    def test_blank_name_records_no_event(self):
        tickets = [make_ticket()]
        save_t, save_e = run_assign(tickets, ["T001", "   "])
        self.assertIsNone(tickets[0]["assigned_to"])
        save_t.assert_not_called()
        save_e.assert_not_called()

    def test_unknown_ticket_records_no_event(self):
        tickets = [make_ticket()]
        save_t, save_e = run_assign(tickets, ["T999"])
        save_t.assert_not_called()
        save_e.assert_not_called()

    def test_resolved_ticket_records_no_event(self):
        tickets = [make_ticket("resolved")]
        save_t, save_e = run_assign(tickets, ["T001"])
        self.assertIsNone(tickets[0]["assigned_to"])
        save_e.assert_not_called()


if __name__ == "__main__":
    unittest.main()