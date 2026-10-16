import unittest
from datetime import datetime, timedelta, timezone

from queues import (
    normalize_text, detect_duplicates, confirm_duplicates,
    get_sla_attention_queue, calculate_metrics,
)

NOW = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)


def make(tid, status="open", due=None, title="Wi-Fi Down", category="network"):
    due = due or NOW + timedelta(hours=1)
    return {"id": tid, "status": status, "priority": "low",
            "title": title, "category": category,
            "deadline": due.isoformat()}


class DuplicateTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(normalize_text(" Wi-Fi   Down "), "wi-fi down")

    def test_matching_unresolved_ticket_is_found(self):
        tickets = [make("T001", title=" Wi-Fi   Down ")]
        self.assertEqual(len(detect_duplicates("network", "wi-fi down", tickets)), 1)

    def test_resolved_or_other_category_is_not_a_duplicate(self):
        tickets = [make("T001", status="resolved"),
                   make("T002", category="hardware")]
        self.assertEqual(detect_duplicates("network", "wi-fi down", tickets), [])

    def test_cancel_returns_false_and_invalid_input_reprompts(self):
        answers = iter(["maybe", "n"])
        result = confirm_duplicates(
            "network", "wi-fi down", [make("T001")],
            input_fn=lambda _: next(answers), print_fn=lambda *a: None)
        self.assertFalse(result)

    def test_confirm_returns_true(self):
        result = confirm_duplicates(
            "network", "wi-fi down", [make("T001")],
            input_fn=lambda _: "y", print_fn=lambda *a: None)
        self.assertTrue(result)


class QueueTests(unittest.TestCase):
    def test_overdue_first_then_earliest_deadline(self):
        tickets = [
            make("T001", due=NOW + timedelta(hours=1)),
            make("T002", due=NOW - timedelta(hours=1)),
            make("T003", due=NOW - timedelta(hours=2)),
        ]
        ids = [t["id"] for t in get_sla_attention_queue(tickets, NOW)]
        self.assertEqual(ids, ["T003", "T002", "T001"])

    def test_same_deadline_ties_break_by_id(self):
        due = NOW - timedelta(hours=1)
        tickets = [make("T002", due=due), make("T001", due=due)]
        ids = [t["id"] for t in get_sla_attention_queue(tickets, NOW)]
        self.assertEqual(ids, ["T001", "T002"])

    def test_resolved_tickets_are_excluded(self):
        tickets = [make("T001", status="resolved", due=NOW - timedelta(hours=1))]
        self.assertEqual(get_sla_attention_queue(tickets, NOW), [])


class MetricsTests(unittest.TestCase):
    def test_each_ticket_counted_once(self):
        tickets = [
            make("T001", "open", NOW - timedelta(hours=1)),
            make("T002", "in_progress", NOW + timedelta(hours=1)),
            make("T003", "resolved", NOW - timedelta(hours=5)),
        ]
        events = [{"action": "ESCALATE"}, {"action": "ESCALATE"},
                  {"action": "START"}]
        m = calculate_metrics(tickets, events, NOW)
        self.assertEqual(
            (m["total"], m["open"], m["in_progress"], m["resolved"],
             m["overdue"], m["escalation_events"]),
            (3, 1, 1, 1, 1, 2))


if __name__ == "__main__":
    unittest.main()