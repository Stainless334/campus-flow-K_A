# CampusFlow Pro: Design Decisions

## 1. Project Overview

CampusFlow Pro is a Python command-line system for managing campus support tickets. It extends the original CampusFlow by adding SLA deadlines, safe escalation of overdue tickets, an audit history, duplicate warnings, an SLA Attention Queue, metrics, and an Engineering Knowledge Lab quiz.

The original features and business rules were kept. New features were added to the existing structure, not built as a replacement.

## 2. Technology Choices

| Choice | Reason |
|---|---|
| Python, standard library only | Easy to learn and maintain, and no outside packages to install or trust. |
| Command-line interface | Keeps the application small and lets the logic be tested without a user interface. |
| JSON file storage | Human-readable, so mentors can inspect it, and no database is needed. |
| `unittest` | Built into Python, and consistent with the original project's tests. |

No web framework was added. This replaces the earlier idea of adding Flask. It is not needed for this stage.

## 3. Data Structures

### Ticket

A ticket is a Python dictionary:

| Field | Meaning |
|---|---|
| `id` | Unique ID such as `T001` |
| `title`, `category`, `urgency`, `affected_users` | Details entered by the user |
| `priority` | Calculated from urgency and affected users |
| `status` | `open`, `in_progress` or `resolved` |
| `assigned_to` | Staff member's name, or `None` |
| `creation_time` | When the ticket was created. Never changes. |
| `sla_start` | When the current SLA cycle began. Changes on reopen. |
| `deadline` | When the current SLA cycle ends |

**Field names and the challenge document.** The challenge document calls the deadline `due_at` and refers to an escalation cycle. This project uses `deadline` for `due_at`, and `sla_start` is what identifies the escalation cycle. The meaning is the same. The names were already in the team's code and storage format, so they were kept to avoid breaking existing behaviour and tests.

### Event (audit history)

Each event is a dictionary:

| Field | Meaning |
|---|---|
| `ticket_id` | The ticket the event belongs to |
| `action` | `CREATE`, `ASSIGN`, `START`, `RESOLVE`, `REOPEN` or `ESCALATE` |
| `actor` | Who did it (`user` or `system`) |
| `timestamp` | UTC time, ISO-8601 |
| `before_status`, `after_status` | The ticket's status before and after the action |
| `details` | Extra information, such as the new assignee or the `sla_start` of an escalation |

The first four fields (`ticket_id`, `action`, `actor`, `timestamp`) are required by `storage.validate_events`. The rest are additional fields that record context.

### Version 2 data file

`data/tickets.json` is one object containing `version`, `tickets`, `events` and `next_id`. Keeping tickets and events together makes one file the single source of truth.

## 4. Module Responsibilities and How They Interact

| Module | Responsibility |
|---|---|
| `main.py` | The menu. Collects input, calls the other modules, prints results. |
| `ticket_creation.py` | Collects ticket details, calculates priority, builds the ticket, runs the duplicate check, records `CREATE`. |
| `workflow.py` | The rules for status changes, reopening and the original unresolved queue. |
| `assign.py` | The assign screen. Records `ASSIGN` after a successful assignment. |
| `sla.py` | Deadline calculation, the overdue check and escalation. |
| `history.py` | Validates and records events, and displays a ticket's history. |
| `queues.py` | Duplicate detection, the SLA Attention Queue and metrics. |
| `knowledge_lab.py` | The Engineering Knowledge Lab quiz. |
| `storage.py` | Validates, loads and saves tickets and events. |
| `report.py`, `ticket_list.py` | The original report, list and find functions. |

**Dependencies flow one way:** `main.py` and the screens call `workflow`, `sla`, `history`, `queues` and `storage`. `sla.py` uses `history.record_event`. `queues.py` uses `sla.is_overdue`. `history.py` imports nothing from the project, so there are no circular imports.

## 5. Key Decisions

### 5.1 Priority calculation

Priority comes from urgency and affected users, checked in order: critical, high, medium, then low. The original rules are unchanged, and the SLA deadline is calculated from the resulting priority.

### 5.2 SLA deadlines and the overdue rule

| Priority | Allowed time |
|---|---|
| critical | 60 minutes |
| high | 240 minutes |
| medium | 1,440 minutes |
| low | 2,880 minutes |

- All times are timezone-aware UTC. Naive datetimes are rejected with a `ValueError`.
- A ticket is overdue only when `now` is **strictly later** than its deadline and it is not resolved. A critical ticket created at 10:00 is not overdue at exactly 11:00.
- `is_overdue` accepts an optional `now`. Tests pass a fixed time, so they do not depend on the real clock. The real clock is read only in `main.py`.

### 5.3 Reopening starts a new SLA cycle

`workflow.reopen_ticket` sets the status to `open`, clears the assignee, sets `sla_start` to the current time, and recalculates the deadline from the priority. `creation_time` is kept, because the ticket was still created once. The new deadline is calculated before any field is changed, so a failure leaves the ticket untouched.

### 5.4 Escalation happens once per SLA cycle

- Each `ESCALATE` event stores the ticket's `sla_start` in `details`.
- Before escalating, `escalate_overdue` checks whether an `ESCALATE` event with the same ticket ID and the same `sla_start` already exists. If so, the ticket is skipped.
- Running the check three times in one cycle therefore creates one event. Reopening changes `sla_start`, so the ticket can be escalated again in the new cycle.
- Escalation never changes the ticket's priority, status or assignee.
- It works on a copy of the events list and extends the real list only after every ticket has been processed. If one ticket is invalid, no events are recorded.

### 5.5 Audit history: record only successful actions

- The code changes a ticket first. Only when that succeeds does it call `record_event`. A rejected action raises an error before the event line, so the history is a true record of what happened.
- `record_event` checks every input before it appends, so a bad call changes nothing.
- The ticket stores its **current** status, and history stores **how it got there**. Status answers "where is it now?" and history answers "what happened, who did it and when?".
- In `assign.py`, the event is built before the ticket is changed. If the event is invalid, the ticket is not modified.

### 5.6 Duplicate warnings warn but do not block

- Titles are normalized by trimming, `casefold()` and collapsing repeated whitespace, so `" Wi-Fi   Down "` matches `"wi-fi down"`.
- A duplicate is an **unresolved** ticket with the same normalized title **and** the same category. Resolved tickets and other categories are ignored.
- The user is shown the matching tickets and asked to confirm. Answering `n` creates nothing: no ticket, no ID and no event. Answering `y` continues.
- It warns instead of blocking because the same problem can really happen twice, and a block would silently lose a legitimate report.
- `detect_duplicates` is separate from the interactive `confirm_duplicates`, so the logic can be tested without typing input.

### 5.7 Two queues for two questions

- **Unresolved Queue (original):** ordered by priority, then ticket number. It answers "what is most important?"
- **SLA Attention Queue:** unresolved tickets, overdue first, then earliest deadline, then ticket ID. It answers "what is about to break its promise?"
- A low-priority ticket that is overdue is last in the first queue and first in the second. The original queue was kept unchanged, and the new one was added beside it.

### 5.8 Metrics

`calculate_metrics` returns total, open, in-progress and resolved counts, the overdue count, and the number of `ESCALATE` events. Each ticket is counted once in exactly one status, so the three status counts always add up to the total. The overdue count is separate, because an open ticket can also be overdue.

### 5.9 Safe storage

- Tickets and events are validated before saving and after loading.
- Saving writes a temporary file, flushes it, and then replaces the real file with `os.replace`. A crash cannot leave a half-written file.
- If the file is damaged, loading raises an error and leaves the existing data alone. It never replaces good data with an empty default.
- An older file that is just a list of tickets is upgraded to version 2 on load.
- `eval()` is never used. The file is parsed with the `json` module.

### 5.10 Engineering Knowledge Lab

The quiz lives in its own module and saves its sessions to a separate JSON file, so running it cannot change tickets or events. Only exact `A`, `B`, `C` or `D` is accepted, and anything else is asked again. Free-text explanations are collected but not auto-graded.

<!-- TODO: confirm the session file name and the participant labels against knowledge_lab.py. -->

## 6. Testing Approach

- `unittest`, run with `python -m unittest discover -s tests -v`.
- Tests use fixed UTC times, mocked storage and mocked input, so they are repeatable and never touch the real data file.
- Key tests: the exact deadline and one minute after it, three escalation runs giving one event, a new escalation after a real reopen, rejected actions adding no event, duplicate normalization, cancelling a duplicate creating nothing, queue ordering and ties, and metrics counting each ticket once.
- Tests for the original features were kept.

## 7. Limitations and Future Improvements

- **Two separate saves.** `save_tickets` and `save_events` are separate writes, so a failure between them could leave a change without its event. Saving both in one operation would fix this.
- **Partial validation.** Validation checks IDs, priority, times and the core event fields, but not every ticket field.
- **No event IDs.** Events are ordered by position in the list and have no unique ID.
- **Exact matching only.** Duplicate detection finds the same normalized title, not similar wording.
- **Manual escalation.** Escalation runs when the user chooses option 9. It could run on a schedule.
- **Data is read at startup.** Edits made to the data file while the program runs are not seen.

## 8. Conclusion

CampusFlow Pro keeps the modular structure and business rules of the original project and adds deadlines, safe escalation, an audit history, duplicate warnings, a deadline-focused queue and metrics. The main design ideas are that history is recorded only after success, that an SLA cycle is identified by `sla_start`, and that stored data is validated before it replaces anything.