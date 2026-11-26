"""Tests for chapter 9: every listing prints what the book shows.
Book: Chapter 9, section 9.1
Run: python -m pytest tests/test_ch09.py
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

OUTPUTS = {
    "ch09/fails.py": (
        "read runs\n"
        "send runs\n"
        "invoke raised: mail server unreachable"
    ),
    "ch09/node_error.py": (
        "read runs\n"
        "send runs\n"
        "invoke raised: mail server unreachable\n"
        "values: {'customer': 'Ana', 'notes': ['read the email']}\n"
        "next: ('send',)\n"
        "task: send | error: ConnectionError('mail server unreachable')\n"
        "type of the error: str\n"
        "copy at step -1 next: ('__start__',)\n"
        "copy at step 0 next: ('read',)\n"
        "copy at step 1 next: ('send',)"
    ),
    "ch09/resume_after_error.py": (
        "read runs\n"
        "send runs\n"
        "invoke raised: mail server unreachable\n"
        "send runs\n"
        "close runs\n"
        "notes: ['read the email', 'sent the reply', 'closed the ticket']\n"
        "copies: 5"
    ),
    "ch09/retry.py": (
        "result: ['sent the reply']\n"
        "attempts: 3\n"
        "invoke raised: mail server unreachable\n"
        "attempts: 3"
    ),
    "ch09/retry_on.py": (
        "ConnectionError 3\n"
        "TimeoutError 1\n"
        "ValueError 1\n"
        "RuntimeError 1\n"
        "MailboxFull 3\n"
        "ValueError with retry_on=ValueError: 3\n"
        "ConnectionError with retry_on=ValueError: 1"
    ),
    "ch09/backoff.py": (
        "attempts: 5\n"
        "waits asked for: [0.5, 1.0, 1.5, 1.5]"
    ),
    "ch09/error_handler.py": (
        "attempts: 3\n"
        "note: read the email\n"
        "note: send failed: mail server unreachable\n"
        "note: a person will answer the customer"
    ),
    "ch09/durability.py": (
        "None up=True: copies=5 next=() then=()\n"
        "None up=False: copies=3 next=('send',) then=()\n"
        "sync up=True: copies=5 next=() then=()\n"
        "sync up=False: copies=3 next=('send',) then=()\n"
        "async up=True: copies=5 next=() then=()\n"
        "async up=False: copies=3 next=('send',) then=()\n"
        "exit up=True: copies=1 next=() then=()\n"
        "exit up=False: copies=1 next=('send',) then=()"
    ),
    "ch09/durability_order.py": (
        "sync: save -1, save 0, read runs, save 1, send runs, save 2\n"
        "exit: read runs, send runs, save 2"
    ),
    "ch09/pitfall_twice.py": (
        "key='': calls=2 mails=2\n"
        "key='ticket-17': calls=2 mails=1"
    ),
    "ch09/pitfall_none.py": (
        "new thread: EmptyInputError\n"
        "send runs\n"
        "second call:\n"
        "copies: 3"
    ),
    "ch09/pitfall_handler.py": (
        "['read the email', 'send failed']\n"
        "TypeError: wrong_name() missing 1 required positional argument: 'err'"
    ),
}


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_shows(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == OUTPUTS[script]
