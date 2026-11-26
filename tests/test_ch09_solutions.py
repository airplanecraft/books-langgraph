"""Tests for chapter 9: self-check scripts and exercise solutions print what the book shows.
Book: Chapter 9, section 9.1
Run: python -m pytest tests/test_ch09_solutions.py
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

OUTPUTS = {
    "ch09/quiz_attempts.py": (
        "4 ['found it']"
    ),
    "ch09/quiz_handler.py": (
        "['order received', 'charge: card declined', 'asked for another card']"
    ),
    "ch09/quiz_copies.py": (
        "1 ('ship',)"
    ),
    "solutions/ch09_ex1.py": (
        "result: ['sent the reply']\n"
        "attempts: 5"
    ),
    "solutions/ch09_ex2.py": (
        "ConnectionError 3\n"
        "ValueError 1"
    ),
    "solutions/ch09_ex3.py": (
        "send ran 2 times\n"
        "1 ('send',)\n"
        "['read the email', 'sent the reply', 'closed the ticket']\n"
        "()"
    ),
}


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_shows(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == OUTPUTS[script]
