"""Interactive Engineering Knowledge Lab for the CampusFlow CLI.

This module runs a 10-question engineering knowledge quiz and saves learning
sessions to a separate JSON file. It does not import or modify ticket records.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


SESSION_FILE = Path(__file__).resolve().parent / "data" / "engineering_knowledge_sessions.json"

QUESTIONS = [
    {
        "id": "Q1",
        "topic": "Critical SLA boundaries",
        "prompt": "A critical ticket is created at 10:00 UTC. At 11:00 UTC, is it overdue?",
        "options": {
            "A": "Yes",
            "B": "No, only strictly after 11:00",
            "C": "Only if assigned",
            "D": "Only if reopened",
        },
        "answer": "B",
        "explanation_prompt": "Explain the difference between 'due' and 'overdue'.",
    },
    {
        "id": "Q2",
        "topic": "Priority calculation order",
        "prompt": "urgency=low and affected_users=10. What priority should the ticket receive?",
        "options": {
            "A": "Critical",
            "B": "High",
            "C": "Medium",
            "D": "Low",
        },
        "answer": "B",
        "explanation_prompt": "Explain which priority rule applies first.",
    },
    {
        "id": "Q3",
        "topic": "Workflow invariants",
        "prompt": "An unassigned open ticket moves directly to in_progress. What should happen?",
        "options": {
            "A": "The transition succeeds",
            "B": "Status changes but history stays unchanged",
            "C": "Reject without changing the ticket or events",
            "D": "Delete the ticket",
        },
        "answer": "C",
        "explanation_prompt": "Explain the invariant the workflow should preserve.",
    },
    {
        "id": "Q4",
        "topic": "Reopening and SLA cycles",
        "prompt": "A resolved high-priority ticket is reopened. Which SLA behavior is correct?",
        "options": {
            "A": "Keep the old due_at always",
            "B": "Start a fresh SLA cycle while preserving created_at",
            "C": "Reset created_at to today's date",
            "D": "Delete previous events",
        },
        "answer": "B",
        "explanation_prompt": "Explain why this SLA behavior is correct.",
    },
    {
        "id": "Q5",
        "topic": "Idempotent escalation",
        "prompt": "An overdue ticket is checked three times within one SLA cycle. How many new ESCALATE events should be created?",
        "options": {
            "A": "Three",
            "B": "Two",
            "C": "One",
            "D": "Zero",
        },
        "answer": "C",
        "explanation_prompt": "Explain idempotency in this situation.",
    },
    {
        "id": "Q6",
        "topic": "Safe JSON loading",
        "prompt": "The saved file contains invalid JSON. What is the safest action?",
        "options": {
            "A": "Replace the data with an empty list",
            "B": "Use eval()",
            "C": "Ignore the problem and continue with partial data",
            "D": "Reject the load and preserve the existing valid state",
        },
        "answer": "D",
        "explanation_prompt": "Explain why your choice is safest.",
    },
    {
        "id": "Q7",
        "topic": "Testing and code review",
        "prompt": "A PR changes SLA calculations but adds no boundary tests. What should a reviewer do?",
        "options": {
            "A": "Approve because it runs locally",
            "B": "Request focused tests and an explanation",
            "C": "Merge and test next week",
            "D": "Ask AI to approve automatically",
        },
        "answer": "B",
        "explanation_prompt": "Explain your review reasoning and which boundary tests matter.",
    },
    {
        "id": "Q8",
        "topic": "Evaluating AI-generated code",
        "prompt": "An assistant says, 'Use eval() to parse stored JSON.' What should you do?",
        "options": {
            "A": "Copy the suggestion",
            "B": "Disable tests",
            "C": "Reject it and use JSON parsing with validation",
            "D": "Share the whole file publicly",
        },
        "answer": "C",
        "explanation_prompt": "Explain how you would verify the safer approach.",
    },
    {
        "id": "Q9",
        "topic": "Duplicate ticket detection",
        "prompt": "Two unresolved tickets share a category and have titles ' Wi-Fi   Down ' and 'wi-fi down'. What should the CLI do?",
        "options": {
            "A": "Silently delete the original",
            "B": "Warn and require confirmation",
            "C": "Silently block the operation forever",
            "D": "Ignore normalization",
        },
        "answer": "B",
        "explanation_prompt": "Explain the trade-off between warning and blocking.",
    },
    {
        "id": "Q10",
        "topic": "Audit log integrity",
        "prompt": "An invalid return/status operation is rejected. What should happen to the event count?",
        "options": {
            "A": "Increase by one",
            "B": "Increase twice",
            "C": "Reset to zero",
            "D": "Stay unchanged",
        },
        "answer": "D",
        "explanation_prompt": "Explain why the event count should behave this way.",
    },
]


def ask_exact_choice(prompt, valid_choices):
    """Ask until the user enters one of the exact allowed uppercase choices."""
    while True:
        choice = input(prompt).strip().upper()
        if choice in valid_choices:
            return choice
        print(f"Invalid input. Enter exactly one of: {', '.join(valid_choices)}.")


def load_session_records(filepath=SESSION_FILE):
    """Load saved sessions without changing ticket data."""
    path = Path(filepath)
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            records = json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        raise ValueError(f"Cannot read learning-session file safely: {error}") from error

    if not isinstance(records, list):
        raise ValueError("Learning-session file must contain a JSON list.")
    return records


def save_session(record, filepath=SESSION_FILE):
    """Append one learning session to its own JSON file."""
    path = Path(filepath)
    records = load_session_records(path)
    records.append(record)

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(records, file, indent=2, ensure_ascii=False)
            file.write("\n")
        temporary_path.replace(path)
    except OSError:
        if temporary_path.exists():
            temporary_path.unlink()
        raise


def run_engineering_knowledge_lab():
    """Run the interactive quiz and save the result as a learning session."""
    print("\n========== ENGINEERING KNOWLEDGE LAB ==========")
    participant = ask_exact_choice(
        "Choose participant label A or B: ",
        ("A", "B"),
    )

    choices = {}
    explanations = {}
    correct_count = 0

    for index, question in enumerate(QUESTIONS):
        print(f"\n{question['id']} — {question['topic']}")
        print(question["prompt"])
        for letter, option_text in question["options"].items():
            print(f"  {letter}. {option_text}")

        choice = ask_exact_choice("Your answer (A/B/C/D): ", ("A", "B", "C", "D"))
        choices[question["id"]] = choice

        if choice == question["answer"]:
            correct_count += 1

        while True:
            if index < 3:
                explanation = input(
                    f"{question['explanation_prompt']} (required): "
                ).strip().upper()
                if explanation:
                    explanations[question["id"]] = explanation
                    break
                print("An explanation is required for this question.")
            else:
                explanation = input(
                    f"{question['explanation_prompt']} "
                    "(optional; press Enter to skip): "
                ).strip().upper()
                if explanation:
                    explanations[question["id"]] = explanation
                break

    revision_topics = [
        question["topic"]
        for question in QUESTIONS
        if choices[question["id"]] != question["answer"]
    ]

    print("\n========== YOUR RESULTS ==========")
    print(f"Participant: {participant}")
    print(f"Score: {correct_count}/10")

    if revision_topics:
        print("Topics to revise:")
        for topic in revision_topics:
            print(f"- {topic}")
    else:
        print("Topics to revise: None — excellent work!")

    print("\nAnswers given:")
    for question in QUESTIONS:
        question_id = question["id"]
        selected = choices[question_id]
        correctness = "Correct" if selected == question["answer"] else "Incorrect"
        print(
            f"{question_id}: You chose {selected} — "
            f"{question['options'][selected]} ({correctness})"
        )

    print("\nYour explanations:")
    for question in QUESTIONS:
        question_id = question["id"]
        explanation = explanations.get(question_id)
        if explanation:
            print(f"{question_id}: {explanation}")
        else:
            print(f"{question_id}: No explanation provided.")

    record = {
        "participant_label": participant,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "choices": choices,
        "score": correct_count,
        "explanations": explanations,
        "revision_topics": revision_topics,
    }

    try:
        save_session(record)
        print(f"\nLearning session saved to: {SESSION_FILE}")
    except (OSError, ValueError) as error:
        print(f"\nCould not save the learning session: {error}")
        print("Your results are shown above, but the session was not saved.")

    input("\nPress Enter to return to the main menu...")


if __name__ == "__main__":
    run_engineering_knowledge_lab()