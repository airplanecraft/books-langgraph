"""Tests for chapter 13: every listing prints what the book shows (offline).
Book: Chapter 13, section 13.1
Run: python -m pytest tests/test_ch13.py
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
PATH = "['classify', 'agent', 'tools', 'agent', '__interrupt__']"

OUTPUTS = {
    "ch13/step1_loop.py": (
        "['HumanMessage', 'AIMessage', 'ToolMessage', 'AIMessage'] | -\n"
        "  last: Hi, A17 has shipped.\n"
        "['HumanMessage'] | handed to a person\n"
        "  last: I want a refund for order B42."
    ),
    "ch13/step2_approve.py": (
        "  ran: " + PATH + "\n"
        "  ran: ['approve', 'send']\n"
        "status: sent | mails: 1"
    ),
    "ch13/step3_fail.py": (
        "  ran: " + PATH + "\n"
        "  raised: mail server unreachable\n"
        "next: ('send',)"
    ),
    "ch13/step4_errors.py": (
        "  ran: " + PATH + "\n"
        "  ran: ['approve', 'send']\n"
        "2 failures: sent | calls: 3 | mail kept: True\n"
        "  ran: " + PATH + "\n"
        "  ran: ['approve', '__error_handler__send', 'to_person']\n"
        "5 failures: handed to a person | calls: 3 | mail kept: False"
    ),
    "ch13/step5_replay.py": (
        "first run: rejected | mails: 0\n"
        "ran again: ['agent', 'tools', 'agent', '__interrupt__']\n"
        "second run: sent | mails: 1"
    ),
    "ch13/optional_parallel.py": (
        "draft ran in super-step 2\n"
        "history ran in super-step 1\n"
        "lookup ran in super-step 1"
    ),
    "ch13/optional_memory.py": (
        "monday -> style rule: short\n"
        "tuesday -> style rule: short\n"
        "wednesday -> style rule: none"
    ),
    "ch13/workflow.py": (
        "  ran: " + PATH + "\n"
        "  ran: ['approve']\n"
        'first draft: "Your order A17 has shipped \\u2014 it went out on 18 November. Let me know if you\'d like help with anything else, like tracking details or delivery estimates."\n'
        "lookup_order {'order_id': 'A17'} -> shipped on 18 November\n"
        'sent | calls: 2 | mails: 1\n'
        'draft: "Your order **A17** has shipped \\u2014 it went out on **18 November**. Let me know if you\'d like help tracking it further or anything else."'
    ),
}


def run(script: str) -> str:
    env = {**os.environ, "OFFLINE": "1"}
    result = subprocess.run([sys.executable, script], cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_shows(script: str) -> None:
    assert run(script) == OUTPUTS[script].strip()


def test_every_file_is_short_and_narrow() -> None:
    for path in sorted((ROOT / "ch13").glob("*.py")):
        lines = path.read_text().splitlines()
        assert len(lines) <= 120, path.name
        assert max(len(line) for line in lines) <= 78, path.name
