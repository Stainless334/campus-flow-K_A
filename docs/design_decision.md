# CampusFlow Design Decisions

## 1. Ticket Data Structure

Each ticket is represented by a Python dictionary containing:

- id
- title
- category
- urgency
- affected_users
- priority
- status
- assigned_to

## 2. Ticket Collection

The application stores tickets in a list of dictionaries.

## 3. Priority Calculation

Priority is calculated using the four rules in the project specification,
checked in the required order.

## 4. Ticket IDs

IDs use the format T001, T002, T003, and so on.

The next ID must be calculated safely from existing ticket IDs
after loading saved data.

## 5. Workflow

Allowed statuses are open, in_progress, and resolved.

An unassigned ticket cannot enter in_progress.

A resolved ticket must be explicitly reopened before further changes.

## 6. Storage

Tickets are saved as JSON.

A missing file means a fresh start.
Malformed JSON must produce a clear error without silently
overwriting the original data.

## 7. Error Handling

Invalid operations must be rejected without leaving partially
updated ticket data.

## 8. Testing

Business logic is tested using Python unittest without
requiring interactive input.

## 9. Team Ownership

Engineer A: ticket creation, validation, and priority calculation.

Engineer B: assignment, lifecycle, queue, and reports.

Both engineers contribute tests and participate in reviews.