"""Tests for chapter 5: exercise solutions, self-check scripts and the listings that need no model.
Book: Chapter 5, section 5.3
Run: python -m pytest tests/test_ch05.py
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

OUTPUTS = {
    "solutions/ch05_ex1.py": "5\n10",
    "solutions/ch05_ex2.py": "ana 3\nben 1",
    "solutions/ch05_ex3.py": ("ana 4 ['human', 'ai', 'human', 'ai']\n"
                              "ben 2 ['human', 'ai']"),
    "ch05/quiz_count.py": "5 checkpoints",
    "ch05/quiz_threads.py": "['b', 'x']",
    "ch05/quiz_merge.py": "{'total': 17, 'label': 'a'}",
    "ch05/no_memory.py": (
        "model node receives 1 ['human']\n"
        "model node receives 3 ['human', 'ai', 'tool']\n"
        "final state holds 4 messages\n"
        "model node receives 1 ['human']\n"
        "final state holds 2 messages"),
    "ch05/lost_on_exit.py": (
        "program 1 - checkpoints before: 0 after: 3\n"
        "program 2 - checkpoints before: 0 after: 3"),
}


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_shows(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == OUTPUTS[script]


def test_the_mistake_scripts_show_the_errors() -> None:
    first = subprocess.run([sys.executable, "ch05/no_thread.py"], cwd=ROOT,
                           capture_output=True, text=True, timeout=60)
    lines = first.stdout.splitlines()
    assert lines[0].startswith("no config: Checkpointer requires one or more")
    assert lines[1] == "no thread_id: KeyError('thread_id')"
    second = subprocess.run([sys.executable, "ch05/no_saver.py"], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert second.stdout.splitlines() == [
        "notes: ['email 2', 'read the email']",
        "get_state: No checkpointer set"]
