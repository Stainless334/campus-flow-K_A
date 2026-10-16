# AI Learning Log: Engineer B

**Project:** CampusFlow Pro
**Role:** Engineer B (audit history, duplicate detection, queues, CLI, Knowledge Lab)
**AI tool used:** Claude
**Dates worked:** October 2026

Each cycle records what I asked, what the AI said, what I checked myself, and what I learned. Evidence comes from my own terminal output and files.

---

## Cycle 1: The audit event format did not match storage

**Question I asked the AI:** How do I build `history.py` so successful actions are recorded as events?

**What the AI gave me:** A `record_event` function that stored each event's type under the key `event_type`.

**What went wrong (evidence):** I ran `python3 main.py`, chose option 6, entered `T001` and the status `in_progress`. The program crashed. I got the same crash when I typed the status as `IN_PROGRESS`:

```
File "/workspaces/campus-flow-K_A/storage.py", line 61, in validate_event
    raise ValueError(f"Event has an invalid {field}.")
ValueError: Event has an invalid action.
```

I then ran option 10 for `T001` and it printed `No history for that ticket.` This showed the crash happened before anything was saved, so my data was not damaged.

**Why it happened:** `storage.validate_events` requires `ticket_id`, `action` and `actor` as non-empty strings, plus a timezone-aware `timestamp`. The AI wrote `history.py` before it had seen `storage.py`, so it guessed the field name.

**What I checked myself:** I pasted `storage.py` to the AI and read `validate_events` to find the required fields. I did not edit `storage.py`, because it is Engineer A's file and defines the data format.

**The fix:** I renamed `event_type` to `action` in `history.py`, and added a test that passes recorded events through `storage.validate_events`.

**Evidence the fix worked:** After the fix, creating a ticket saved this event in `data/tickets.json`:

```json
"ticket_id": "T002",
"action": "CREATE",
"actor": "user",
"timestamp": "2026-10-16T00:47:49+00:00",
"before_status": null,
"after_status": "open",
"details": { "priority": "critical" }
```

The file saved without a validation error, so the event format now matches storage.

**What I learned:** The module that stores data decides what a valid record looks like. Code that creates records must match that format. When the AI could not see my other file, it guessed, and the guess was wrong. A test that connects the two modules stops the mismatch coming back.

---

## Cycle 2: Escalation found overdue tickets but never recorded them

**Question I asked the AI:** Why does "Escalate Overdue Tickets" in the menu not work?

**What the AI found by reading my `sla.py`:** `escalate_overdue` looped over the tickets and called `is_overdue`, then checked `sla_start`, but never created an event. The line `events.extend(new_events)` sat outside the loop, so `new_events` was always empty and the menu always said there was nothing to escalate.

**What the AI proposed:**
- Record an `ESCALATE` event for each overdue ticket and store the ticket's `sla_start` in the event's `details`.
- Skip a ticket if an `ESCALATE` event with the same `sla_start` already exists. This is how one escalation per SLA cycle is enforced.
- Work on a copy of the events list, so an error leaves the real history unchanged.

**What I checked myself:**
- I read the old function and confirmed its loop body ended after the `sla_start` check.
- I pasted `workflow.py` and confirmed `reopen_ticket` sets a new `sla_start` and `deadline` and keeps `creation_time`. This is why a reopened ticket can be escalated again.
- I read `main.py` and found that `escalate_menu` calls `is_overdue`, which was not imported. That would have crashed option 9 with a `NameError`.

**Test evidence:** I created `tests/test_escalation.py` with 8 tests: exactly at the deadline is not overdue, 61 minutes is overdue, three runs give one event, a new cycle after reopening gives a second event, the ticket is not changed, old events are preserved, an error leaves events unchanged, and one test that uses the real `workflow.reopen_ticket`. My first attempt to run it failed with `ModuleNotFoundError: No module named 'test_escalation'`. The cause was in my directory listing: the file was named `test_escalaation.py` (two "a"s) and lives in `tests/`.

**Not yet verified on my machine:** the passing test run and the menu test. Run these and paste the results here before submitting:

```bash
mv tests/test_escalaation.py tests/test_escalation.py
python -m unittest discover -s tests -p "test_escalation.py" -v
```

Result: **[paste the last lines, `Ran 8 tests ... OK` if it passes]**

**What I learned:** Running the same operation several times should not create repeated side effects. This is called idempotency. To make it safe I needed something that identifies the SLA cycle, and `sla_start` does that. Reopening changes `sla_start`, so it starts a new cycle. I also learned that a unit test passing proves the function works, but not that the menu works, because the menu code is separate and needs its own manual check.

---

## Cycle 3: Finding a missing file and a wrong test location

**Situation:** `git status` showed `knowledge_lab.py` as modified. `git diff -- knowledge_lab.py` showed all 291 lines removed, and `wc -l knowledge_lab.py` printed `0`. `main.py` imports `run_engineering_knowledge_lab` from that file, so an empty file would crash the whole program.

**Question I asked the AI:** How do I recover the file without losing work?

**What the AI said:** Git still holds the last committed version, so I can restore it with `git restore knowledge_lab.py`. It also told me it could not recreate my exact 291 lines, because it had never seen them, and that anything it wrote would be a different file.

**What I checked myself:** I did not run `git reset` or `git checkout` first, because they could have thrown away work. I read the diff first to see what had changed.

**Not yet verified on my machine:** that the restore worked. Run these and paste the results:

```bash
git restore knowledge_lab.py
wc -l knowledge_lab.py
git status
```

Result: **[paste the line count; it should be about 291]**

**What I learned:** `git diff` shows exactly what changed before anything is overwritten, and committed code can be recovered. I also learned to check where files really live: `ls test_*.py` found nothing because all my tests are in the `tests/` folder, so the right command is `python -m unittest discover -s tests`.

---

## Smaller problems I solved

| Problem | Evidence | Cause | Fix |
|---|---|---|---|
| Invalid status rejected | Typed `start` in option 6: `Error: Invalid status. Choose open, in_progress, or resolved.` | `start` is not one of the three allowed statuses | Use `in_progress`. The rejection recorded no event, as required. |
| Tests not found | `ls test_*.py` printed `No such file or directory` | Tests are in `tests/`, not the root | Use `discover -s tests` |
| Commands split across two lines | `bash: t_escalation: command not found` | I pressed Enter in the middle of a command | Type the command on one line |
| Missing import | Found by reading `main.py` | `escalate_menu` used `is_overdue` but only imported `escalate_overdue` | Added `is_overdue` to the import from `sla` |

---

## Where the AI was wrong or limited

- It wrote `history.py` with the wrong field name because it had not seen `storage.py` (Cycle 1).
- It cannot run my tests or see my files. Statements like "it should pass" were not proof until I ran the tests myself.
- It said it could not reproduce my lost 291-line file from memory, which was correct. Git was the right tool.

## Independent experiments I ran without AI help

**Not yet done.** Run the time experiment from the challenge guide and paste the real output:

```bash
python3 -c "from datetime import datetime, timezone, timedelta; start = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc); due = start + timedelta(minutes=60); print('Created:', start.isoformat()); print('Due:', due.isoformat())"
```

Result: **[paste output; expect Created 10:00 and Due 11:00]**

## Honesty note

Evidence above comes from my own terminal output, my directory listings, and my `data/tickets.json`. Items marked "not yet verified" stay that way until I run the command and paste the real result.