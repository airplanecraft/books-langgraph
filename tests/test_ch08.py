"""Tests for chapter 8: the scripts print what the book shows.
Book: Chapter 8, section 8.1
Run: python -m pytest tests/test_ch08.py
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

OUTPUTS = {
    "ch08/ticket.py": (
        "draft runs\n"
        "SENT\n"
        "general ['classified', 'drafted', 'sent']"),
    "ch08/history.py": (
        "draft runs\n"
        "SENT\n"
        "general ['classified', 'drafted', 'sent']\n"
        "3 loop () general\n"
        "2 loop ('send',) general\n"
        "1 loop ('draft',) general\n"
        "0 loop ('classify',) None\n"
        "-1 input ('__start__',) None\n"
        "[True, True, True, True]\n"
        "general ['checkpoint_id', 'checkpoint_ns', 'thread_id']"),
    "ch08/replay_interrupt.py": (
        "review starts\n"
        "review starts\n"
        "approved\n"
        "review starts\n"
        "asked again: True ('review',)\n"
        "review starts\n"
        "edited"),
    "ch08/fork.py": (
        "draft runs\n"
        "SENT\n"
        "general ['classified', 'drafted', 'sent']\n"
        "update ('escalate',) billing\n"
        "thread now waits at: ('escalate',)\n"
        "ESCALATED\n"
        "billing ['classified', 'passed to a person']\n"
        "3 loop () billing\n"
        "2 update ('escalate',) billing\n"
        "3 loop () general\n"
        "2 loop ('send',) general\n"
        "1 loop ('draft',) general\n"
        "0 loop ('classify',) None\n"
        "-1 input ('__start__',) None\n"
        "ESCALATED\n"
        "['classified', 'passed to a person', 'classified', 'passed to a person']"),
}


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_shows(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == OUTPUTS[script]
