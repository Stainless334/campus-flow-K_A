
"""
CampusFlow ticket storage.

This module saves tickets to a JSON file and loads them
when the application starts.
"""

import json
import os
from pathlib import Path


# The project root is the folder containing main.py.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Store saved tickets in the project's data folder.
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "tickets.json"


def validate_tickets(tickets):
    """
    Check that tickets have the correct basic structure
    and that every ticket has a unique ID.
    """

    if not isinstance(tickets, list):
        raise ValueError("Ticket data must be a list.")

    seen_ids = set()

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary.")

        ticket_id = ticket.get("id")

        if not isinstance(ticket_id, str) or not ticket_id.strip():
            raise ValueError("Every ticket must have a valid ID.")

        if ticket_id in seen_ids:
            raise ValueError(
                f"Duplicate ticket ID found: {ticket_id}"
            )

        seen_ids.add(ticket_id)


def save_tickets(tickets, filepath=None):
    """
    Save tickets to a JSON file.

    The temporary file helps protect the previous saved file
    if writing the new data fails before the replacement.
    """

    validate_tickets(tickets)

    if filepath is None:
        filepath = DEFAULT_DATA_FILE

    filepath = Path(filepath)

    # Create the folder if it does not exist.
    filepath.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = filepath.with_name(filepath.name + ".tmp")

    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(tickets, file, indent=4)

        # Replace the old file only after writing succeeds.
        os.replace(temporary_path, filepath)

    except (OSError, TypeError, ValueError) as error:
        # Do not leave a temporary file behind after a failure.
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass

        raise ValueError(
            f"Could not save tickets: {error}"
        ) from error


def load_tickets(filepath=None):
    """
    Load tickets from a JSON file.

    If the file does not exist, return an empty list.
    If the file is damaged or its data is invalid, raise
    an error instead of silently discarding saved information.
    """

    if filepath is None:
        filepath = DEFAULT_DATA_FILE

    filepath = Path(filepath)

    # A first-time user may not have a saved file yet.
    if not filepath.exists():
        return []

    try:
        with filepath.open("r", encoding="utf-8") as file:
            tickets = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Cannot load tickets: the JSON file is damaged "
            f"or invalid ({error})."
        ) from error

    except OSError as error:
        raise ValueError(
            f"Cannot read the ticket file: {error}"
        ) from error

    validate_tickets(tickets)

    return tickets