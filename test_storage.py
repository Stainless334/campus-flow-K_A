import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import load_tickets, save_tickets


class TestTicketStorage(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.filepath = Path(self.temp_directory.name) / "tickets.json"

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_save_and_load_tickets(self):
        tickets = [
            {
                "id": "T001",
                "title": "Internet problem",
                "status": "open",
                "priority": "high",
            }
        ]

        save_tickets(tickets, self.filepath)
        loaded_tickets = load_tickets(self.filepath)

        self.assertEqual(loaded_tickets, tickets)

    def test_missing_file_returns_empty_list(self):
        loaded_tickets = load_tickets(self.filepath)

        self.assertEqual(loaded_tickets, [])

    def test_empty_list_can_be_saved(self):
        save_tickets([], self.filepath)

        loaded_tickets = load_tickets(self.filepath)

        self.assertEqual(loaded_tickets, [])

    def test_duplicate_ids_are_rejected(self):
        tickets = [
            {"id": "T001", "title": "First ticket"},
            {"id": "T001", "title": "Second ticket"},
        ]

        with self.assertRaisesRegex(ValueError, "Duplicate"):
            save_tickets(tickets, self.filepath)

    def test_invalid_json_raises_error(self):
        self.filepath.write_text(
            "{this is not valid JSON",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "JSON file"):
            load_tickets(self.filepath)

    def test_duplicate_ids_in_saved_file_are_rejected(self):
        tickets = [
            {"id": "T001", "title": "First ticket"},
            {"id": "T001", "title": "Second ticket"},
        ]

        self.filepath.write_text(
            json.dumps(tickets),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "Duplicate"):
            load_tickets(self.filepath)


if __name__ == "__main__":
    unittest.main()
