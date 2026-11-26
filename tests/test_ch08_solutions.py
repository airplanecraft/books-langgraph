"""Tests for chapter 8: the self-check runs and the exercise solutions.
Book: Chapter 8, section 8.5
Run: python -m pytest tests/test_ch08_solutions.py
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

OUTPUTS = {
    "ch08/quiz_rerun.py": "['clean', 'store'] 8",
    "ch08/quiz_count.py": "7",
    "ch08/quiz_fork.py": (
        "{'items': ['a', 'x'], 'status': 'edited'} ('two',)\n"
        "('three',)\n"
        "['a', 'x', 'c']"),
    "solutions/ch08_ex1.py": "draft 1, send 2",
    "solutions/ch08_ex2.py": (
        "draft runs\n"
        "SENT\n"
        "SENT\n"
        "['classified', 'sent']\n"
        "update 1 fork 0"),
    "solutions/ch08_ex3.py": (
        "draft runs\n"
        "SENT\n"
        "ESCALATED\n"
        "billing ['classified', 'passed to a person']\n"
        "draft runs\n"
        "SENT\n"
        "general ['classified', 'drafted', 'sent']\n"
        "copies 11"),
}


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_shows(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == OUTPUTS[script]
