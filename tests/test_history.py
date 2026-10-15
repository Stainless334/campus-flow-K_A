import unittest
from datetime import datetime, timezone

from history import record_event, get_ticket_history
from storage import validate_events

T = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)


class HistoryTests(unittest.TestCase):
    def test_event_sequence_is_recorded_in_order(self):
        events = []
        steps = [
            ("CREATE", None, "open"),
            ("ASSIGN", "open", "open"),
            ("START", "open", "in_progress"),
            ("RESOLVE", "in_progress", "resolved"),
            ("REOPEN", "resolved", "open"),
        ]
        for action, before, after in steps:
            record_event(events, "T1", action, "system", T, before, after)
        self.assertEqual(
            [e["action"] for e in events],
            ["CREATE", "ASSIGN", "START", "RESOLVE", "REOPEN"],
        )

    def test_events_pass_storage_validation(self):
        events = []
        record_event(events, "T1", "START", "user", T, "open", "in_progress")
        validate_events(events)  # raises ValueError if the format is wrong

    def test_invalid_action_appends_nothing(self):
        events = []
        with self.assertRaises(ValueError):
            record_event(events, "T1", "DELETE", "system", T, "open", "open")
        self.assertEqual(events, [])

    def test_naive_timestamp_appends_nothing(self):
        events = []
        with self.assertRaises(ValueError):
            record_event(events, "T1", "CREATE", "system",
                         datetime(2026, 10, 14, 10, 0), None, "open")
        self.assertEqual(events, [])

    def test_history_only_returns_that_ticket(self):
        events = []
        record_event(events, "T1", "CREATE", "a", T, None, "open")
        record_event(events, "T2", "CREATE", "a", T, None, "open")
        self.assertEqual(len(get_ticket_history(events, " t1 ")), 1)


if __name__ == "__main__":
    unittest.main()