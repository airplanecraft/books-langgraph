"""Tests for chapter 2: exercise solutions and the facts the chapter states.
Book: Chapter 2, section 2.6
Run: python -m pytest tests/test_ch02.py
"""
import operator
import subprocess
import sys
from pathlib import Path
from typing import Annotated, TypedDict

import pytest
from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, StateGraph

ROOT = Path(__file__).parent.parent

SOLUTIONS = {
    "solutions/ch02_ex1.py":
        "dropped: ['categroy']\n{'customer': 'Ana', 'category': 'unknown'}",
    "solutions/ch02_ex2.py": "2 It was delayed.",
    "solutions/ch02_ex3.py": "['billing', 'urgent', 'refund']",
}


@pytest.mark.parametrize("script", SOLUTIONS)
def test_solution_prints_what_the_exercise_asks_for(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == SOLUTIONS[script]


def run(schema: type, node, start: dict) -> dict:
    builder = StateGraph(schema)
    builder.add_node("node", node)
    builder.add_edge(START, "node")
    builder.add_edge("node", END)
    return builder.compile().invoke(start)


class Plain(TypedDict):
    category: str


class Added(TypedDict):
    notes: Annotated[list[str], operator.add]


def test_unknown_keys_are_dropped_and_types_are_not_checked() -> None:
    node = lambda state: {"category": 42, "mood": "angry"}  # noqa: E731
    start = {"category": "x", "channel": "email"}
    assert run(Plain, node, start) == {"category": 42}


def test_empty_and_none_change_nothing_a_list_is_an_error() -> None:
    start = {"category": "x"}
    assert run(Plain, lambda state: None, start) == start
    assert run(Plain, lambda state: {}, start) == start
    with pytest.raises(InvalidUpdateError):
        run(Plain, lambda state: ["x"], {"category": "x"})


def test_the_reducer_also_applies_to_the_input() -> None:
    node = lambda state: {"notes": ["b"]}  # noqa: E731
    assert run(Added, node, {"notes": ["a"]}) == {"notes": ["a", "b"]}


def test_returned_keys_can_be_checked_against_the_schema() -> None:
    class State(TypedDict):
        category: str

    good = {"category": "billing"}
    typo = {"categroy": "billing"}
    assert set(good) <= set(State.__annotations__)
    assert not set(typo) <= set(State.__annotations__)
