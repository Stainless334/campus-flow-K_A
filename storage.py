import copy
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from sla import calculate_due_at, sla_duration

DEFAULT_DATA_FILE = Path(__file__).resolve().parent / "data" / "tickets.json"
VERSION = 2
TIME_FIELDS = ("creation_time", "sla_start", "deadline")


def _valid_time(value):
    try:
        return datetime.fromisoformat(value).utcoffset() is not None
    except (TypeError, ValueError):
        return False


def _valid_priority(value):
    return isinstance(value, str) and value in sla_duration


def _next_number(tickets):
    numbers = [int(t["id"][1:]) for t in tickets
               if t["id"].startswith("T") and t["id"][1:].isdigit()]
    return max(numbers, default=0) + 1


def validate_tickets(tickets):
    if not isinstance(tickets, list):
        raise ValueError("Ticket data must be a list.")
    seen = set()
    for t in tickets:
        if not isinstance(t, dict):
            raise ValueError("Each ticket must be a dictionary.")
        tid = t.get("id")
        if not isinstance(tid, str) or not tid.strip():
            raise ValueError("Every ticket must have a valid ID.")
        if tid in seen:
            raise ValueError(f"Duplicate ticket ID found: {tid}")
        seen.add(tid)
        if not isinstance(t.get("status"), str) or not t["status"]:
            raise ValueError(f"Ticket {tid} has an invalid status.")
        if not _valid_priority(t.get("priority")):
            raise ValueError(f"Ticket {tid} has an invalid priority.")
        for field in TIME_FIELDS:
            if not _valid_time(t.get(field)):
                raise ValueError(f"Ticket {tid} has an invalid {field}.")


def validate_events(events):
    if not isinstance(events, list):
        raise ValueError("Event data must be a list.")
    for e in events:
        if not isinstance(e, dict):
            raise ValueError("Each event must be a dictionary.")
        for field in ("ticket_id", "action", "actor"):
            if not isinstance(e.get(field), str) or not e[field]:
                raise ValueError(f"Event has an invalid {field}.")
        if not _valid_time(e.get("timestamp")):
            raise ValueError("Event has an invalid timestamp.")


def validate_document(doc):
    validate_tickets(doc["tickets"])
    validate_events(doc["events"])
    n = doc["next_id"]
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("next_id must be a positive integer.")


def _upgrade(tickets, now):
    tickets = copy.deepcopy(tickets)
    for t in tickets:
        if not isinstance(t, dict):
            raise ValueError("Each ticket must be a dictionary.")
        if not _valid_time(t.get("creation_time")):
            t["creation_time"] = now.isoformat()
        if not _valid_time(t.get("sla_start")):
            t["sla_start"] = t["creation_time"]
        if not _valid_time(t.get("deadline")):
            if not _valid_priority(t.get("priority")):
                raise ValueError(f"Ticket {t.get('id')} has an invalid priority.")
            start = datetime.fromisoformat(t["sla_start"])
            t["deadline"] = calculate_due_at(t["priority"], start).isoformat()
    return tickets


def _read(filepath=None):
    path = Path(filepath or DEFAULT_DATA_FILE)
    if not path.exists():
        return {"version": VERSION, "tickets": [], "events": [], "next_id": 1}

    try:
        with path.open("r", encoding="utf-8") as file:
            raw = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"Cannot load data: damaged JSON ({error}).") from error
    except OSError as error:
        raise ValueError(f"Cannot read the data file: {error}") from error

    if isinstance(raw, list):
        tickets = _upgrade(raw, datetime.now(timezone.utc))
        validate_tickets(tickets)
        doc = {"version": VERSION, "tickets": tickets, "events": [],
               "next_id": _next_number(tickets)}
    elif isinstance(raw, dict):
        if raw.get("version") != VERSION:
            raise ValueError(f"Unsupported data version: {raw.get('version')}")
        missing = {"tickets", "events", "next_id"} - raw.keys()
        if missing:
            raise ValueError(f"Data file is missing: {sorted(missing)}")
        doc = {key: raw[key] for key in ("version", "tickets", "events", "next_id")}
    else:
        raise ValueError("Data file must contain a version-2 object.")

    validate_document(doc)
    return doc


def _write(doc, filepath=None):
    validate_document(doc)
    path = Path(filepath or DEFAULT_DATA_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        with tmp.open("w", encoding="utf-8") as file:
            json.dump(doc, file, indent=4)
            file.flush()
            os.fsync(file.fileno())
        os.replace(tmp, path)
    except (OSError, TypeError, ValueError) as error:
        tmp.unlink(missing_ok=True)
        raise ValueError(f"Could not save data: {error}") from error


def load_tickets(filepath=None):
    return _read(filepath)["tickets"]


def load_events(filepath=None):
    return _read(filepath)["events"]


def load_next_id(filepath=None):
    return _read(filepath)["next_id"]


def save_tickets(tickets, filepath=None):
    doc = _read(filepath)
    validate_tickets(tickets)
    doc["tickets"] = tickets
    doc["next_id"] = max(doc["next_id"], _next_number(tickets))
    _write(doc, filepath)


def save_events(events, filepath=None):
    doc = _read(filepath)
    doc["events"] = events
    _write(doc, filepath)