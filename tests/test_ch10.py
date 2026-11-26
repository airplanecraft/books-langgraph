"""Tests for chapter 10: exercise solutions and the quiz runs.
Book: Chapter 10, section 10.8
Run: python -m pytest tests/test_ch10.py
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

OUTPUTS = {
    "solutions/ch10_ex1.py": "draft: super-step 3, notes seen 5",
    "solutions/ch10_ex2.py": "['from order', 'from plan']",
    "solutions/ch10_ex3.py":
        "['A17: shipped', 'B42: delayed', 'C03: shipped']\n2 shipped",
    "ch10/quiz_steps.py": "['join:3', 'join:4']",
    "ch10/quiz_limit.py": "smallest limit that finishes: 5",
    "ch10/quiz_send.py": "[1, 2, 3] 6",
    "ch10/quiz_waits.py": "['close:4']",
    "ch10/quiz_defer.py": "list 0\ndefer 1",
    "ch10/quiz_total.py": "115",
    "ch10/parallel_limit.py": "limit 3 GraphRecursionError\nlimit 4 finished",
}


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_says(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == OUTPUTS[script]


def run(script: str) -> list[str]:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    return result.stdout.splitlines()


def test_fan_out_puts_three_nodes_in_one_super_step() -> None:
    lines = run("ch10/parallel.py")
    assert [line.split(",")[0] for line in lines] == [
        "read: super-step 1", "order: super-step 2", "plan: super-step 2",
        "shipping: super-step 2", "draft: super-step 3"]
    assert lines[1:4] == [line for line in lines[1:4] if "notes seen 1" in line]


def test_the_chain_needs_five_super_steps() -> None:
    lines = run("ch10/sequential.py")
    assert [line.split(",")[0].split(": ")[1] for line in lines] == [
        f"super-step {number}" for number in range(1, 6)]


def test_separate_edges_run_the_join_twice_and_the_other_forms_once() -> None:
    lines = run("ch10/fan_in.py")
    assert lines.count("   draft: super-step 3, notes seen 3") == 1
    assert [line for line in lines if "draft" in line] == [
        "   draft: super-step 3, notes seen 3",
        "   draft: super-step 4, notes seen 5",
        "   draft: super-step 4, notes seen 4",
        "   draft: super-step 4, notes seen 4"]


def test_only_the_deferred_node_runs_once_in_both_cases() -> None:
    lines = run("ch10/defer_optional.py")
    counts = [line.rsplit("draft ran ", 1)[1].split()[0] for line in lines]
    assert counts == ["0", "1", "1", "1", "2", "1"]


def test_send_pitfalls_print_what_the_book_shows() -> None:
    lines = run("ch10/pitfall_send.py")
    assert lines[0] == "1 ['A']" and "InvalidUpdateError" in lines[1]
    assert lines[3] == "None [('__start__', '__end__')]"


def test_a_list_of_literals_as_return_type_draws_no_conditional_edge() -> None:
    from typing import Literal, TypedDict

    from langgraph.graph import END, START, StateGraph

    class State(TypedDict):
        log: list[str]

    def pick(state: State) -> list[Literal["a", "b"]]:
        return ["a"]

    def make(destinations):
        builder = StateGraph(State)
        builder.add_node("a", lambda state: {"log": ["a"]})
        builder.add_node("b", lambda state: {"log": ["b"]})
        builder.add_conditional_edges(START, pick, destinations)
        builder.add_edge("a", END)
        builder.add_edge("b", END)
        edges = builder.compile().get_graph().edges
        return {(e.source, e.target) for e in edges if e.conditional}

    assert make(None) == {("__start__", "__end__")}
    assert make(["a", "b"]) == {("__start__", "a"), ("__start__", "b")}
