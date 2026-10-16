# CampusFlow Pro

CampusFlow Pro is a command-line help-desk ticket system for campus IT issues. Users can create tickets, assign them to staff, track them through a workflow, and print reports. Every ticket has a deadline based on its priority (an SLA), overdue tickets can be escalated, and every successful action is written to an audit history. Tickets and history are saved to disk, so they are still there the next time the program runs.

CampusFlow Pro extends the original CampusFlow project. The original features and rules still apply.

## Features

- Create tickets with a title, category, urgency and number of affected users
- Automatic ticket IDs (`T001`, `T002`, ...) and automatic priority calculation
- Duplicate warning: if an unresolved ticket has the same title and category, the user is warned and asked to confirm
- List all tickets or view one ticket by ID
- Assign tickets to staff members
- Change ticket status with enforced rules (open -> in_progress -> resolved)
- Reopen resolved tickets, which starts a new SLA cycle
- SLA deadlines in UTC, based on priority
- Safe escalation of overdue tickets (one escalation per SLA cycle)
- Audit history of every successful action
- Original unresolved queue (by priority) and SLA Attention Queue (by deadline risk)
- Metrics summary and the original report
- Engineering Knowledge Lab: an interactive 10-question quiz
- Automatic saving and loading (JSON file)

## Requirements

- Python 3.8 or newer (developed and tested on Python 3.14)
- No external packages are needed. Only the standard library is used.

## Getting Started

```bash
git clone https://github.com/Stainless334/campus-flow-K_A.git
cd campus-flow-K_A
python3 main.py
```

## Using the Menu

```
_______ CAMPUSFLOW PRO _______
    1. Create Ticket
    2. List All Tickets
    3. View One Ticket
    4. Assign Ticket
    5. Print Report
    6. Change Ticket Status
    7. Reopen Ticket
    8. Unresolved Queue
    9. Escalate Overdue Tickets
    10. View Ticket History
    11. Engineering Knowledge Lab
    12. SLA Attention Queue
    13. Metrics
    0. Exit
```

Type a number and press Enter. The menu keeps running until you choose `0`.

**Example session:** create a ticket (1), assign it (4), start work (6 -> `in_progress`), resolve it (6 -> `resolved`), reopen it (7), then view its history (10).

## Ticket Fields

| Field | Description |
|---|---|
| `id` | Generated automatically, e.g. `T001` |
| `title` | Short description of the problem (cannot be blank) |
| `category` | Network, Hardware, Software or Other |
| `urgency` | low, medium or high |
| `affected_users` | Positive whole number |
| `priority` | Calculated automatically (see below) |
| `status` | open, in_progress or resolved |
| `assigned_to` | Staff member's name, or empty if unassigned |
| `creation_time` | UTC time the ticket was created. Never changes. |
| `sla_start` | UTC time the current SLA cycle began. Changes on reopen. |
| `deadline` | UTC time the current SLA cycle ends |

## Priority Rules

| Condition | Priority |
|---|---|
| High urgency and 10 or more affected users | critical |
| High urgency, or 10 or more affected users | high |
| Medium urgency, or 3 or more affected users | medium |
| Anything else | low |

## Status Workflow

```
open --> in_progress --> resolved
  ^                          |
  +-------- reopen ----------+
```

- A ticket must be assigned before work can start.
- A ticket cannot skip from `open` straight to `resolved`.
- A resolved ticket is locked until it is reopened.
- Reopening sets the ticket back to `open`, clears the assignee, and starts a new SLA cycle. `creation_time` is kept.
- A rejected action changes nothing and records no history event.

## SLA Rules

Each ticket gets a deadline when its SLA cycle starts:

| Priority | Allowed time |
|---|---|
| critical | 60 minutes |
| high | 240 minutes (4 hours) |
| medium | 1,440 minutes (24 hours) |
| low | 2,880 minutes (48 hours) |

- All times are timezone-aware UTC.
- A ticket is **overdue only when the current time is strictly later than its deadline** and it is not resolved. A critical ticket created at 10:00 is not overdue at 11:00 exactly, but is overdue at 11:01.
- The deadline is always calculated from the priority, never typed in.

## Escalation Rules

- Option 9 checks every ticket and records an `ESCALATE` event for each overdue ticket.
- A ticket is escalated **at most once per SLA cycle**. Each `ESCALATE` event stores the ticket's `sla_start`, and a ticket that already has an event for its current `sla_start` is skipped.
- Running option 9 repeatedly does not create duplicate events. It reports how many tickets were newly escalated and how many had already been escalated.
- Reopening a ticket gives it a new `sla_start`, so it can be escalated again if it becomes overdue in the new cycle.
- Escalation never changes a ticket's priority, status or assignee.
- If any ticket fails validation, nothing is recorded.

## Audit History

Every successful action records an event: `CREATE`, `ASSIGN`, `START`, `RESOLVE`, `REOPEN` or `ESCALATE`. An event is recorded only after the action succeeds.

| Event field | Description |
|---|---|
| `ticket_id` | The ticket the event belongs to |
| `action` | One of the six actions above |
| `actor` | Who did it (`user` or `system`) |
| `timestamp` | UTC time of the event |
| `before_status`, `after_status` | The ticket's status before and after |
| `details` | Extra information, e.g. the assignee or the `sla_start` of an escalation |

Option 10 shows one ticket's history in the order it happened. The current status is stored on the ticket, and the history records how it got there.

## Duplicate Detection

When creating a ticket, the title is normalized (trimmed, case-folded and with repeated spaces collapsed) and compared with the title and category of every unresolved ticket. For example, `" Wi-Fi   Down "` and `"wi-fi down"` match.

- If a match exists, the matching tickets are shown and the user is asked whether to continue.
- Answering `n` cancels creation. No ticket, ID or event is created.
- Answering `y` creates the ticket normally. A warning never blocks a legitimate repeat incident.
- Tickets in a different category, and resolved tickets, are not treated as duplicates.

## Queues and Metrics

- **Unresolved Queue (option 8):** the original queue. Sorted by priority (critical, high, medium, low), then by ticket number.
- **SLA Attention Queue (option 12):** unresolved tickets with overdue ones first, then the earliest deadline, then ticket ID. Each ticket is marked `OVERDUE` or `on time`.
- **Metrics (option 13):** total, open, in progress and resolved counts, overdue count, and the number of escalation events. Each ticket is counted once in exactly one status.

A low-priority ticket that is already overdue is last in the Unresolved Queue and first in the SLA Attention Queue. That is why both exist.

## Engineering Knowledge Lab

Option 11 runs an interactive quiz of 10 multiple-choice engineering questions.

- The user chooses a participant label, answers each question with exactly `A`, `B`, `C` or `D`, and invalid input is asked again.
- The user writes a short explanation for at least three answers. Explanations are not graded automatically.
- At the end the score out of 10, topics to revise, the answers given and the explanations are shown.
- A session record (participant, UTC timestamp, choices, score, explanations) is saved to a separate JSON file.
- Running the quiz never changes any ticket or event.

<!-- TODO: confirm the participant labels, the number of required explanations, and the session file name/location against knowledge_lab.py. -->

## Data Storage

Tickets and history are saved to `data/tickets.json` in the project folder (created on first save) and loaded each time the program starts. The file is local data and is ignored by Git.

The file is a version 2 document:

```json
{
    "version": 2,
    "tickets": [],
    "events": [],
    "next_id": 1
}
```

- An older file that is just a list of tickets is upgraded automatically on load.
- Saving is crash-safe: data is written to a temporary file first, then replaces the old file with `os.replace`.
- Tickets and events are validated on load and save: unique ticket IDs, valid priority, timezone-aware times, and events with a ticket ID, action, actor and timestamp.
- If `tickets.json` is damaged or invalid, the program raises an error instead of silently discarding your data.

## Project Structure

| File | Purpose |
|---|---|
| `main.py` | Menu and program entry point |
| `ticket_creation.py` | Creates tickets, generates IDs, calculates priority, duplicate check |
| `ticket_list.py` | Lists and finds tickets |
| `assign.py` | Assigns a ticket to staff from the menu |
| `workflow.py` | Status changes, reopening and the unresolved queue |
| `sla.py` | SLA deadlines, overdue check and escalation |
| `history.py` | Records and displays audit events |
| `queues.py` | Duplicate detection, SLA Attention Queue and metrics |
| `knowledge_lab.py` | The Engineering Knowledge Lab quiz |
| `report.py` | The original ticket report |
| `storage.py` | Validates, saves and loads tickets and events |
| `tests/` | Automated tests |
| `docs/` | Design decisions and learning documentation |

## Running the Tests

```bash
python -m unittest discover -s tests -v
```

Tests use fixed UTC times and mocked storage, so they do not touch your real data file.

## Team

- Ikwuje Emmanuel (Engineer B: history, queues, duplicate detection, CLI, Knowledge Lab)
- Abdulrauf Raifu (Engineer A: SLA, escalation, storage)

<!-- TODO: confirm names and roles with your teammate. -->

## Contributing

1. Pull the latest code: `git switch main && git pull origin main`
2. Create a branch: `git switch -c my-feature`
3. Make your changes and run the tests
4. Add only the files you changed, then commit
5. Push the branch and open a pull request into `main`
6. A teammate reviews and approves before merging

Never commit directly to `main`.

## Known Limitations

- Tickets and events are saved in two separate steps. If the second save failed, the file could briefly hold a change without its matching event.
- Validation checks ticket IDs, priority and times, but not every field. A hand-edited `tickets.json` with a missing field may still cause errors in reports.
- The program reads the data file when it starts, so edits made to the file while it is running are not seen.
- Events have no unique event ID.
- Duplicate detection compares exact normalized titles, not similar wording.
- Escalation is run manually from the menu and does not notify anyone.

## Future Improvements

- Save tickets and events together in one write
- Add unique event IDs
- Run escalation automatically on a schedule
- Detect similar (not just identical) titles