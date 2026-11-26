"""Tests for chapter 13: self-check runs, exercise solutions, pitfalls and the stream mode.
Book: Chapter 13, section 13.4
Run: python -m pytest tests/test_ch13_more.py
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

OUTPUTS = {
    "ch13/quiz_refund.py": "path: ['classify', 'to_person']",
    "ch13/quiz_replay_tools.py": "ran again: ['tools', 'agent', '__interrupt__']",
    "ch13/quiz_fallback.py": "handed to a person | 3 attempts",
    "ch13/pitfall_replay.py": "send calls: 2 | mails kept: 1",
    "ch13/pitfall_thread.py": (
        "thread holds: T1 | 4 messages\n"
        "thread holds: T2 | 8 messages\n"
        "mails: ['T2']"
    ),
    "solutions/ch13_ex1.py": "sent | calls: 4",
    "solutions/ch13_ex2.py": (
        "status: sent\n"
        "mail: Hi Ana, A17 ships Friday."
    ),
    "solutions/ch13_ex3.py": "['shipped on 18 November', 'about 2 days']",
}


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_shows(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == OUTPUTS[script].strip()


def test_the_retry_waits_are_tiny() -> None:
    """The step files use a wait of 0.01 seconds and no jitter."""
    for name in ("step4_errors.py", "workflow.py"):
        source = (ROOT / "ch13" / name).read_text()
        assert "initial_interval=0.01, jitter=False" in source


def test_every_stream_call_names_its_mode() -> None:
    for path in (ROOT / "ch13").glob("*.py"):
        for line in path.read_text().splitlines():
            if "graph.stream(" in line:
                assert "stream_mode=" in line, (path.name, line)


def test_the_loop_has_a_small_recursion_limit() -> None:
    source = (ROOT / "ch13" / "workflow.py").read_text()
    assert '"recursion_limit": 10' in source


def test_no_listing_sends_real_mail() -> None:
    """The mail service is a dictionary; nothing imports a mail or network library."""
    for path in (ROOT / "ch13").glob("*.py"):
        source = path.read_text()
        for word in ("smtplib", "requests", "httpx", "socket", "import langchain\n"):
            assert word not in source, (path.name, word)
