"""Tests for chapter 7: every script prints what the book shows (the model script runs offline).
Book: Chapter 7, section 7.2
Run: python -m pytest tests/test_ch07.py
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

OUTPUTS = {
    "ch07/no_question.py": "REFUND SENT for A17\nI have refunded order A17.",
    "ch07/pause.py": (
        "review starts\n"
        "keys: ['customer', 'draft', '__interrupt__']\n"
        "list 1 Interrupt\n"
        "question: Send this reply?\n"
        "next: ('review',)\n"
        "pending: Send this reply?\n"
        "checkpoints: 2"),
    "ch07/resume.py": (
        "review starts\n"
        "keys: ['customer', 'draft', '__interrupt__']\n"
        "list 1 Interrupt\n"
        "question: Send this reply?\n"
        "next: ('review',)\n"
        "pending: Send this reply?\n"
        "checkpoints: 2\n"
        "review starts\n"
        "review got: approved\n"
        "result: {'customer': 'Ana', 'draft': 'Hi Ana, your refund is on its "
        "way.', 'status': 'approved'}\n"
        "next: ()\n"
        "checkpoints: 3"),
    "ch07/edit_reject.py": (
        "SENT to Ana\n"
        "t1 -> sent | Hi Ana, B42 is delayed.\n"
        "SENT to Ana\n"
        "t2 -> sent | Hi Ana, B42 ships Friday.\n"
        "t3 -> rejected | Hi Ana, B42 is delayed.\n"
        "t4 -> rejected | Hi Ana, B42 is delayed."),
    "ch07/ask_in_tool.py": (
        "refund_order starts for A17\n"
        "t1 asked: Refund order A17?\n"
        "refund_order starts for A17\n"
        "REFUND SENT for A17\n"
        "t1 tool message: refund sent for A17\n"
        "refund_order starts for B42\n"
        "t2 asked: Refund order B42?\n"
        "refund_order starts for B42\n"
        "t2 tool message: a person refused the refund"),
    "ch07/two_tools.py": (
        "refund_order starts for A17\n"
        "refund_order starts for A17\n"
        "REFUND SENT for A17\n"
        "note_order started 2 times"),
    "ch07/pitfall_rerun.py": (
        "look_up runs\n"
        "review starts\n"
        "shown to the person: Draft one.\n"
        "review starts\n"
        "saved in the state: Draft two."),
    "ch07/fix_rerun.py": (
        "draft runs\n"
        "review starts\n"
        "shown to the person: Draft one.\n"
        "review starts\n"
        "saved in the state: Draft one."),
    "ch07/two_questions.py": (
        "collect starts\n"
        "asked: Which order?\n"
        "collect starts\n"
        "first answer: B42\n"
        "asked: Which reason?\n"
        "collect starts\n"
        "first answer: B42\n"
        "second answer: late\n"
        "final: ['B42', 'late']"),
    "ch07/no_checkpointer.py": (
        "paused: Send this reply?\n"
        "RuntimeError: Cannot use Command(resume=...) without checkpointer"),
    "ch07/pitfall_resume.py": (
        "look_up runs\n"
        "review starts\n"
        "look_up runs\n"
        "review starts\n"
        "plain invoke on ana: Send this reply?\n"
        "look_up runs\n"
        "review starts\n"
        "resume=None: UnboundLocalError ('review',)\n"
        "review starts\n"
        "other code: yes"),
    "ch07/pitfall_except.py": (
        "caught: GraphInterrupt\n"
        "result: {'status': 'no answer'}\n"
        "next: ()"),
}


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_shows(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == OUTPUTS[script]


def test_the_model_script_replays_offline() -> None:
    env = {**os.environ, "OFFLINE": "1"}
    result = subprocess.run([sys.executable, "ch07/approve.py"], cwd=ROOT,
                            capture_output=True, text=True, timeout=60, env=env)
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert lines[0] == "question: Send this reply?"
    assert lines[2] == "next: ('review',)"
    assert lines[3:] == ["SENT to Ana", "status: sent"]
