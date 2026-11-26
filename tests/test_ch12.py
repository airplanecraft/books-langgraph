"""Tests for chapter 12: what every script prints, and the exercise solutions.
Book: Chapter 12, section 12.1
Run: python -m pytest tests/test_ch12.py
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

OUTPUTS = {
    "ch12/forget.py": (
        "monday {'customer': 'Ana', 'greeting': 'Hello, Ana.'} 3 checkpoints\n"
        "tuesday {'greeting': 'Hello, (unknown).'} 3 checkpoints"),
    "ch12/store_basics.py": (
        "{'tone': 'short'} prefs ('users', 'ana')\n"
        "{'tone': 'formal'}\nNone\nNone"),
    "ch12/share.py": (
        "monday ana: short (4 checkpoints)\n"
        "tuesday ana: short (4 checkpoints)\n"
        "wednesday ben: none saved (4 checkpoints)\n"
        "{'user': 'ana', 'note': 'ana: short'}"),
    "ch12/namespaces.py": (
        "ana tab   ['users/ana/prefs', 'users/ana/address']\n"
        "all users ['users/ana/prefs', 'users/ana/address', "
        "'users/ben/prefs']\n"
        "no such   []\nfiltered  ['users/ana/prefs']\ntypo      None\n"
        "tuple     None\nstring    ('u', 's', 'e', 'r', 's')\n"
        "log       10 12"),
    "ch12/context_state.py": (
        "Hello, ana.\nHello, ana.\n"
        "['ana', 'ana', 'ana', 'ana', 'ana', None]"),
    "ch12/context.py": (
        "{'greeting': 'Hello, ana.'}\n{'greeting': 'Hello, ben.'}\n"
        "{'greeting': 'Hello, ana.'}"),
    "ch12/context_frozen.py": (
        "refused: cannot assign to field 'user_id'\n"
        "{'greeting': 'Hello, ana.'}"),
    "ch12/where.py": (
        "monday ['visit 1'] | store count: 1\n"
        "monday ['visit 1', 'visit 2'] | store count: 2\n"
        "tuesday ['visit 3'] | store count: 3\n"
        "['notes'] ['thread_id', 'checkpoint_ns', 'checkpoint_id']"),
    "ch12/pitfall_query.py": "[('prefs', None), ('address', None)]",
    "ch12/pitfall_missing.py": (
        "{'done': True}\n"
        "AttributeError: 'NoneType' object has no attribute 'user_id'\n"
        "AttributeError: 'NoneType' object has no attribute 'put'"),
    "ch12/quiz_prefix.py": "2 items",
    "ch12/quiz_counter.py": "[3]",
    "ch12/quiz_context.py": "{'seen': 'nothing'}",
    "solutions/ch12_ex1.py": "{'tone': 'long'}\n2",
    "solutions/ch12_ex2.py": "ana 2\nben 1",
    "solutions/ch12_ex3.py": "ana -> Answer in this style: short.\nben -> no instruction",
}


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_shows(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == OUTPUTS[script]


def test_remember_replays_offline_with_the_instruction_from_the_store() -> None:
    env = {**os.environ, "OFFLINE": "1"}
    result = subprocess.run([sys.executable, "ch12/remember.py"], cwd=ROOT,
                            capture_output=True, text=True, timeout=60,
                            env=env)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "instruction from the store: Answer in this style: "
        "one short, polite sentence.",
        "model receives 2 messages",
        "monday last message is an AIMessage",
        "instruction from the store: Answer in this style: "
        "one short, polite sentence.",
        "model receives 2 messages",
        "tuesday last message is an AIMessage",
        "model receives 1 messages",
        "wednesday last message is an AIMessage"]
