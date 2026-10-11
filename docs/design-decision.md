# CampusFlow – Design Decisions

## 1. Project Overview
CampusFlow is a Python CLI ticket management system designed to help campus support teams create, view, and assign support tickets.

## 2. Technology Choices
- **Python:** Easy to learn and maintain.
- **CLI:** Keeps the application simple and lightweight.
- **unittest:** Used to test features and verify expected behavior.

## 3. Ticket Data Structure
Each ticket is stored as a Python dictionary containing:
- `id`
- `title`
- `category`
- `urgency`
- `affected_users`
- `priority`
- `status`
- `assigned_to`

A list stores the tickets created during the program's execution.

## 4. Ticket ID and Validation
Tickets use unique IDs such as `T001` and `T002`. User inputs are validated to reduce invalid data, including empty ticket titles and invalid selections.

## 5. Priority Calculation
Ticket priority is calculated using urgency and the number of affected users:

- **Critical:** High urgency and at least 10 affected users.
- **High:** High urgency or at least 10 affected users.
- **Medium:** Medium urgency or at least 3 affected users.
- **Low:** Otherwise.

The rules are checked in order to ensure the correct priority is assigned.

## 6. Ticket Status and Assignment
New tickets start with an `open` status and no assigned staff member (`None`). The assignment feature allows tickets to be assigned to staff and rejects invalid assignments.

A complete ticket status workflow may be added in the future.

## 7. Code Organization
The project is divided into separate modules:

- `ticket_create.py` — Creates tickets and calculates priority.
- `ticket_list.py` — Lists and displays tickets.
- `assign.py` — Handles ticket assignment.

This structure makes the code easier to understand, test, and maintain.

## 8. Testing
Python's `unittest` framework is used to test ticket creation, listing, viewing, and assignment. Mocking is used to simulate user input where necessary.

## 9. Limitations and Future Improvements
It has no framework yet
Future improvements include:
- Addition of flask and other modules
## Conclusion
CampusFlow uses a modular Python structure, dictionary-based ticket records, priority rules, and automated tests to provide a foundation for managing campus support requests.