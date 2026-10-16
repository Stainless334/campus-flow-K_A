import unittest
from datetime import datetime, timedelta, timezone

import workflow
from sla import escalate_overdue

T0 = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)


def make_ticket(sla_start=T0, status="open"):
    return {
        "id": "T001", "status": status, "priority": "critical",
        "assigned_to": "IKWUJE",
        "sla_start": sla_start.isoformat(),
        "deadline": (sla_start + timedelta(minutes=60)).isoformat(),
    }


class EscalationTests(unittest.TestCase):
    def test_not_escalated_exactly_at_deadline(self):
        events = []
        new = escalate_overdue([make_ticket()], events,
                               T0 + timedelta(minutes=60), "system")
        self.assertEqual(new, [])

    def test_escalated_one_minute_after_deadline(self):
        events = []
        new = escalate_overdue([make_ticket()], events,
                               T0 + timedelta(minutes=61), "system")
        self.assertEqual(len(new), 1)
        self.assertEqual(events[0]["action"], "ESCALATE")

    def test_three_runs_in_same_cycle_give_one_event(self):
        events, tickets = [], [make_ticket()]
        now = T0 + timedelta(minutes=90)
        for _ in range(3):
            escalate_overdue(tickets, events, now, "system")
        self.assertEqual(len(events), 1)

    def test_new_cycle_after_reopen_allows_new_escalation(self):
        events, tickets = [], [make_ticket()]
        escalate_overdue(tickets, events, T0 + timedelta(minutes=90), "system")
        new_start = T0 + timedelta(hours=5)
        tickets[0] = make_ticket(sla_start=new_start)
        escalate_overdue(tickets, events,
                         new_start + timedelta(minutes=61), "system")
        self.assertEqual(len(events), 2)

    def test_ticket_is_not_changed_by_escalation(self):
        ticket = make_ticket()
        before = dict(ticket)
        escalate_overdue([ticket], [], T0 + timedelta(minutes=90), "system")
        self.assertEqual(ticket, before)

    def test_previous_events_are_preserved(self):
        old = {"ticket_id": "T999", "action": "START", "actor": "u",
               "timestamp": T0.isoformat()}
        events = [old]
        escalate_overdue([make_ticket()], events,
                         T0 + timedelta(minutes=90), "system")
        self.assertEqual(events[0], old)
        self.assertEqual(len(events), 2)

    def test_error_leaves_events_unchanged(self):
        bad = make_ticket()
        del bad["sla_start"]
        events = []
        with self.assertRaises(ValueError):
            escalate_overdue([bad], events,
                             T0 + timedelta(minutes=90), "system")
        self.assertEqual(events, [])

    def test_real_reopen_allows_a_new_escalation(self):
        events = []
        ticket = make_ticket()
        tickets = [ticket]

        escalate_overdue(tickets, events, T0 + timedelta(minutes=90), "system")
        self.assertEqual(len(events), 1)

        workflow.change_ticket_status(tickets, "T001", "in_progress")
        workflow.change_ticket_status(tickets, "T001", "resolved")
        reopened_at = T0 + timedelta(hours=5)
        workflow.reopen_ticket(tickets, "T001", now=reopened_at)

        escalate_overdue(tickets, events,
                         reopened_at + timedelta(minutes=60), "system")
        self.assertEqual(len(events), 1)
        later = reopened_at + timedelta(minutes=61)
        escalate_overdue(tickets, events, later, "system")
        escalate_overdue(tickets, events, later, "system")
        self.assertEqual(len(events), 2)


if __name__ == "__main__":
    unittest.main()