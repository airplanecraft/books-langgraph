"""More tests for chapter 8: the other scripts, the offline run, and the claims the text makes.
Book: Chapter 8, section 8.3
Run: python -m pytest tests/test_ch08_more.py
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

OUTPUTS = {
    "ch08/as_node.py": (
        "draft runs\n"
        "SENT\n"
        "general ['classified', 'drafted', 'sent']\n"
        "None -> ('escalate',)\n"
        "classify -> ('escalate',)\n"
        "draft -> ('send',)"),
    "ch08/write_reply.py": (
        "draft runs\n"
        "SENT\n"
        "general ['classified', 'drafted', 'sent']\n"
        "SENT\n"
        "['classified', 'sent'] True"),
    "ch08/pitfall_reducer.py": (
        "draft runs\n"
        "SENT\n"
        "general ['classified', 'drafted', 'sent']\n"
        "['classified', 'checked by hand']\n"
        "['checked by hand']"),
    "ch08/pitfall_newest.py": (
        "draft runs\n"
        "SENT\n"
        "general ['classified', 'drafted', 'sent']\n"
        "next: ()\n"
        "copies: 5 -> 6\n"
        "newest now: fork"),
}


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_shows(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == OUTPUTS[script]


def test_the_model_script_runs_offline() -> None:
    env = {**os.environ, "OFFLINE": "1"}
    result = subprocess.run([sys.executable, "ch08/checkpoint_replay.py"],
                            cwd=ROOT, capture_output=True, text=True,
                            timeout=60, env=env)
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert lines[:2] == ["draft runs", "SENT"]
    assert lines[3:6] == [
        "--- run again from the copy before draft", "draft runs", "SENT"]
    assert lines[7:] == [
        "4 loop ()", "3 loop ('send',)", "2 fork ('draft',)", "3 loop ()",
        "2 loop ('send',)", "1 loop ('draft',)", "0 loop ('classify',)",
        "-1 input ('__start__',)", "get_state: 4 loop ()"]
