"""Tests for chapter 6: exercise solutions and what each stream mode gives.
Book: Chapter 6, section 6.6
Run: python -m pytest tests/test_ch06.py
"""
import subprocess
import sys
from pathlib import Path

import pytest

from ch06_helpers import QUESTION, agent, counting_graph

ROOT = Path(__file__).parent.parent

SOLUTIONS = {
    "solutions/ch06_ex1.py": "values updates values updates values updates values",
    "solutions/ch06_ex2.py":
        "packing A17\npacking B42\npacking C99\npacked 3",
    "solutions/ch06_ex3.py":
        "asks for lookup_order\ntool says: delayed: waiting for stock\n"
        "answer: Order B42 is delayed: waiting for stock.",
}


@pytest.mark.parametrize("script", SOLUTIONS)
def test_solution_prints_what_the_exercise_asks_for(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == SOLUTIONS[script]


def test_the_last_values_item_is_what_invoke_returns() -> None:
    last = list(agent().stream(QUESTION, stream_mode="values"))[-1]
    final = agent().invoke(QUESTION)
    assert [m.type for m in last["messages"]] == [m.type for m in final["messages"]]
    assert [m.content for m in last["messages"][1:]] == [m.content for m in final["messages"][1:]]


def test_values_gives_the_input_first_then_one_item_per_writing_super_step() -> None:
    kinds = [[m.type for m in state["messages"]]
             for state in agent().stream(QUESTION, stream_mode="values")]
    assert kinds == [["human"], ["human", "ai"], ["human", "ai", "tool"],
                     ["human", "ai", "tool", "ai"]]


@pytest.mark.parametrize("writes, values_items", [
    ([True, True, True], 4), ([True, False, True], 3), ([False, False], 1),
    ([False, True, False, True], 3)])
def test_values_skips_a_super_step_that_writes_nothing(writes, values_items) -> None:
    graph = counting_graph(writes)
    assert len(list(graph.stream({"count": 0}, stream_mode="values"))) == values_items
    assert len(list(graph.stream({"count": 0}, stream_mode="updates"))) == len(writes)


def test_a_node_without_changes_shows_up_in_updates_as_none() -> None:
    items = list(counting_graph([True, False]).stream({"count": 0}, stream_mode="updates"))
    assert items == [{"n0": {"count": 1}}, {"n1": None}]


def test_the_default_mode_is_updates() -> None:
    graph = counting_graph([True, True])
    assert list(graph.stream({"count": 0})) == list(graph.stream({"count": 0}, stream_mode="updates"))


def test_a_list_of_modes_gives_pairs_even_with_one_mode() -> None:
    graph = counting_graph([True])
    assert list(graph.stream({"count": 0}, stream_mode=["updates"])) == [("updates", {"n0": {"count": 1}})]


def test_custom_items_come_before_the_update_of_their_node() -> None:
    graph = counting_graph([True, True], [["a", "b"], ["c"]])
    modes = [m for m, _ in graph.stream({"count": 0}, stream_mode=["custom", "updates"])]
    assert modes == ["custom", "custom", "updates", "custom", "updates"]
    assert list(graph.stream({"count": 0}, stream_mode="custom")) == ["a", "b", "c"]


def test_invoke_ignores_the_stream_writer() -> None:
    assert counting_graph([True], [["a"]]).invoke({"count": 0}) == {"count": 1}
