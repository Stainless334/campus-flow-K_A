# AI Learning Log: Engineer A

**Project:** CampusFlow Pro  
**Role:** Engineer A (SLA management, overdue detection, storage)  
**AI tool used:** ChatGPT  
**Dates worked:** October 2026

Each cycle records what I asked, what the AI suggested, what I checked, and what I learned. Test results are not claimed until verified on my machine.

---

## Cycle 1: Implementing SLA deadlines

**Question I asked the AI:** How do I calculate ticket deadlines based on priority and detect overdue tickets?

**What the AI gave me:** Guidance for implementing `calculate_due_at()` and `is_overdue()` in `sla.py`, using Python's `datetime`, `timedelta`, and timezone-aware UTC timestamps.

**What I implemented:** My `sla.py` calculates deadlines using these rules:

- Critical: 60 minutes
- High: 240 minutes
- Medium: 1,440 minutes
- Low: 2,880 minutes

The `is_overdue()` function checks a ticket's deadline, validates its timestamp, and excludes resolved and closed tickets.

**What I checked myself:** I reviewed the functions and confirmed that invalid priorities, missing deadlines, and timezone-naive timestamps raise `ValueError`.

**Testing status:** I prepared a `test_sla.py` test suite covering deadlines, invalid inputs, and overdue detection. The test results have not yet been verified.

**What I learned:** An SLA defines how quickly a ticket should be handled. Timezone-aware timestamps help avoid ambiguity, while injecting `now` makes time-dependent functions easier to test consistently.

---

## Cycle 2: Planning escalation and preventing duplicate events

**Question I asked the AI:** How should I test and implement the overdue-ticket escalation process?

**What the AI suggested:** Record an escalation event when a ticket becomes overdue and prevent repeated checks from creating duplicate events during the same SLA cycle.

**What I checked myself:** I reviewed my `sla.py` and confirmed that `escalate_overdue()` still contains `pass`.

**Current status:** Escalation is not yet implemented. I need to confirm the event format in `history.py` and the team's requirements before completing it.

**What I learned:** Idempotency means repeating an operation should not produce unintended duplicate effects. Escalation must also respect the ticket's current SLA cycle.

---

## Smaller problems and lessons

| Problem | What I learned |
|---|---|
| Invalid priority values | Validate inputs before calculating deadlines. |
| Missing or invalid deadlines | Handle malformed ticket data explicitly. |
| Exact deadline comparisons | `now > due_at` means a ticket is not overdue at the exact deadline. |
| Testing time-dependent functions | Supplying a fixed `now` makes test results predictable. |
| Incomplete escalation function | Verify the existing event structure before integrating modules. |

---

## Where the AI was limited

- AI-generated tests are not proof that the implementation works until I execute them.
- Suggestions about escalation must match the team's existing event format and workflow.
- I must inspect my project files and verify results rather than assume suggested changes are correct.

## Independent experiments

**Status:** Not yet documented.

I will record an independent experiment after running it and capturing the actual terminal output.

## What I learned overall

This work has helped me understand SLA calculations, UTC timestamps, input validation, overdue detection, and unit testing. I also learned to distinguish between code that has been written, code that has been tested, and code that has been fully integrated.

**Honesty note:** The SLA deadline and overdue-detection functions are implemented in my current `sla.py`. The escalation function remains unfinished, and the prepared tests still need to be run. I have not claimed unverified results as successful evidence.