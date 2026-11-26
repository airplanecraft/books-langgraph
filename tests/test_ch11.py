"""Tests for chapter 11: every script prints what the book shows (the model script replays offline).
Book: Chapter 11, section 11.1
Run: python -m pytest tests/test_ch11.py
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest
ROOT = Path(__file__).parent.parent

OUTPUTS = {
    "ch11/subgraph_shared.py": (
        "find sees ['order_id']\n"
        "{'order_id': 'A17', 'status': 'shipped on 18 November', 'source': 'order system'}\n"
        "find sees ['order_id']\n"
        "{'customer': 'Ana', 'order_id': 'A17', 'status': 'shipped on 18 November', 'reply': 'Hi Ana, order A17 is shipped on 18 November.'}\n"
        "['customer', 'order_id', 'reply', 'status']"),
    "ch11/pitfall_duplicate.py": (
        "{'notes': ['start', 'checked']}\n"
        "{'notes': ['start', 'start', 'checked']}\n"
        "['start', 'checked']"),
    "ch11/subgraph_transform.py": (
        "{'customer': 'Ana', 'order_ref': 'B42', 'notes': ['start', 'B42: delayed']}"),
    "ch11/subgraph_memory.py": (
        "None visits [1, 1, 1]\n"
        "True visits [1, 2, 1]\n"
        "False visits [1, 1, 1]"),
    "ch11/subgraph_interrupt.py": (
        "  ask starts\n"
        "asked: Refund order A17?\n"
        "  ask starts\n"
        "  ask got yes\n"
        "{'order_id': 'A17', 'answer': 'yes'}"),
    "ch11/subgraph_rerun.py": (
        "  call_orders starts\n"
        "  ask starts\n"
        "asked: Refund order B42?\n"
        "  call_orders starts\n"
        "  ask starts\n"
        "{'order_id': 'B42', 'answer': 'no'}"),
    "ch11/handoff_basic.py": (
        "['start', 'support: pass to billing', 'billing: refund noted']\n"
        "[('__start__', 'support'), ('billing', '__end__'), ('support', 'billing')]"),
    "ch11/handoff.py": (
        "  support reads ['human']\n"
        "  support reads ['human', 'ai', 'tool']\n"
        "  billing reads ['human', 'ai', 'tool']\n"
        "  billing reads ['human', 'ai', 'tool', 'ai', 'tool']\n"
        "human | Please refund my order A17.\n"
        "ai | transfer_to_billing\n"
        "tool | Passed to billing.\n"
        "ai | refund_order\n"
        "tool | refund started for A17\n"
        "ai | Your refund for A17 is on its way."),
    "ch11/handoff_update.py": (
        "pair\n"
        "  support reads ['human']\n"
        "  support reads ['human', 'ai', 'tool']\n"
        "  billing reads ['human', 'ai', 'tool']\n"
        "nothing\n"
        "  support reads ['human']\n"
        "  support reads ['human', 'ai', 'tool']\n"
        "  billing reads ['human']\n"
        "all\n"
        "  support reads ['human']\n"
        "  support reads ['human', 'ai', 'tool']\n"
        "  billing reads ['human', 'ai', 'tool', 'ai', 'tool']"),
    "ch11/handoff_pitfalls.py": (
        "['start', 'support: pass to billing', 'billing: refund noted']\n"
        "[('__start__', 'support'), ('billing', '__end__'), ('support', 'billing')]\n"
        "['support: pass to billing', 'billing: refund noted'] [('__start__', 'support'), ('support', '__end__')]\n"
        "['support: pass to billing', 'billing: refund noted', 'report: ran'] [('__start__', 'support'), ('billing', '__end__'), ('report', '__end__'), ('support', 'billing'), ('support', 'report')]\n"
        "compile: Found edge ending at unknown node `billing`\n"
        "alone: ParentCommand"),
    "ch11/handoff_two_calls.py": (
        "  support reads ['human']\n"
        "  billing reads ['human', 'ai', 'tool']\n"
        "  open requests: ['call_1']"),
    "ch11/quiz_double.py": (
        "['a', 'a', 'b']"),
    "ch11/quiz_memory.py": (
        "[1, 2, 3, 1]"),
    "ch11/quiz_rerun.py": (
        "wrapper 2 ask 2"),
    "ch11/quiz_handoff.py": (
        "['s', 'b', 'c']"),
}
SOLUTIONS = {
    "solutions/ch11_ex1.py": "[1, 2, 3]",
    "solutions/ch11_ex2.py": "{'notes': ['start', 'checked']}",
    "solutions/ch11_ex3.py": "billing\nsupport",
}


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_shows(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.rstrip() == OUTPUTS[script]


@pytest.mark.parametrize("script", SOLUTIONS)
def test_solution_prints_the_done_line(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == SOLUTIONS[script]


def test_the_real_model_script_replays_offline() -> None:
    env = {**os.environ, "OFFLINE": "1"}
    result = subprocess.run([sys.executable, "ch11/handoff_real.py"], cwd=ROOT,
                            capture_output=True, text=True, timeout=60, env=env)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-6:] == [
        "human []", "ai ['transfer_to_billing']", "tool []",
        "ai ['refund_order']", "tool []", "ai []"]
