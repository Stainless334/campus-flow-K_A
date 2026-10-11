# campus-flow-K_A

# CampusFlow

CampusFlow is a command-line help-desk ticket system for campus IT issues. Users can create tickets, assign them to staff, track progress through a workflow, and print reports. Tickets are saved to disk, so they are still there the next time the program runs.

## Features

- Create tickets with a title, category, urgency and number of affected users
- Automatic ticket IDs (`T001`, `T002`, ...) and automatic priority calculation
- List all tickets or view one ticket by ID
- Assign tickets to staff members
- Change ticket status with enforced rules (open -> in_progress -> resolved)
- Reopen resolved tickets
- View the unresolved queue, sorted by priority
- Print a report of totals by status and priority
- Automatic saving and loading of tickets (JSON file)

## Requirements

- Python 3.8 or newer
- No external packages are needed to run the app
- `pytest` is optional (the tests also work with `unittest`)

## Getting Started

bash
git clone https://github.com/Stainless334/campus-flow-K_A.git
cd campus-flow-K_A
python3 main.py


## Using the Menu

_______ CAMPUSFLOW _______
    1. Create Ticket
    2. List All Tickets
    3. View One Ticket
    4. Assign Ticket
    5. Print Report
    6. Change Ticket Status
    7. Reopen Ticket
    8. Unresolved Queue
    9. Exit


Type a number and press Enter.

**Example session:** create a ticket (1), assign it to a staff member (4), start work on it (6 -> `in_progress`), resolve it (6 -> `resolved`), then print the report (5).

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

## Priority Rules

| Condition | Priority |
|---|---|
| High urgency and 10 or more affected users | critical |
| High urgency, or 10 or more affected users | high |
| Medium urgency, or 3 or more affected users | medium |
| Anything else | low |

## Status Workflow


open --> in_progress --> resolved
  ^                          |
  +-------- reopen ----------+


- A ticket must be assigned before work can start.
- A ticket cannot skip from `open` straight to `resolved`.
- A resolved ticket is locked until it is reopened. Reopening sets it back to `open` and clears the assignee.
- The unresolved queue is sorted by priority (critical, high, medium, low), then by ticket number.

## Data Storage

Tickets are saved automatically to `data/tickets.json` in the project folder (created on first save) and loaded each time the program starts. Delete the file to start fresh. It is local test data and is ignored by Git.

Saving is crash-safe: data is written to a temporary file first and only replaces the old file once writing succeeds. Tickets are validated when saved and loaded:

- Ticket data must be a list of dictionaries
- Every ticket needs a non-empty string ID
- Ticket IDs must be unique

If `tickets.json` is damaged, the program raises an error instead of silently discarding your tickets.

## Project Structure

| File | Purpose |
|---|---|
| `main.py` | Menu and program entry point |
| `ticket_creation.py` | Creates tickets, generates IDs, calculates priority |
| `ticket_list.py` | Lists and finds tickets |
| `assign.py` | Assigns a ticket to staff from the menu |
| `workflow.py` | Status changes, reopening and the unresolved queue |
| `report.py` | Ticket statistics and report printing |
| `storage.py` | Validates, saves and loads tickets |
| `test_workflow.py` | Tests for workflow rules |
| `test_report.py` | Tests for reports |
| `test_storage.py` | Tests for saving and loading |

## Running the Tests

bash
python3 -m unittest discover


or, if you have pytest:

bash
python3 -m pytest


## Team

- iorniem Kenneth 
- <colleague's name: Abdulrauf Raifu>

## Contributing

1. Pull the latest code: git switch main && git pull origin main
2. Create a branch: `git switch -c my-feature
3. Make your changes and run the tests
4. Add only the files you changed, then commit
5. Push the branch and open a pull request into main
6. A teammate reviews and merges it

Never commit directly to main

## Known Limitations

- Validation checks ticket IDs only, not other fields. A hand-edited tickets.json with a missing status or priority will crash the report.