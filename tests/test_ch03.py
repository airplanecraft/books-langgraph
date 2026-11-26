"""Tests for chapter 3: exercise solutions and the facts the chapter states.
Book: Chapter 3, section 3.6
Run: python -m pytest tests/test_ch03.py
"""
import subprocess
import sys
from pathlib import Path
from typing import Literal, TypedDict

import pytest
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph

ROOT = Path(__file__).parent.parent

SOLUTIONS = {
    "solutions/ch03_ex1.py":
        "billing | Hi Ana, we are checking the charge.\n"
        "shipping | Hi Ben, we are tracking your parcel.\n"
        "other | Hi Cy, thanks for your email.",
    "solutions/ch03_ex2.py": "3 False",
    "solutions/ch03_ex3.py": "GraphRecursionError\n{'count': 5}",
}


@pytest.mark.parametrize("script", SOLUTIONS)
def test_solution_prints_what_the_exercise_asks_for(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == SOLUTIONS[script]


class State(TypedDict):
    count: int


def add_one(state: State) -> dict:
    return {"count": state["count"] + 1}


def stop_at(runs: int):
    def route(state: State) -> Literal["add_one", "__end__"]:
        return END if state["count"] >= runs else "add_one"
    return route


def plain(state: State):
    return END if state["count"] >= 3 else "add_one"


def loop(route, node=add_one):
    builder = StateGraph(State)
    builder.add_node("add_one", node)
    builder.add_edge(START, "add_one")
    builder.add_conditional_edges("add_one", route)
    return builder.compile()


def edges(graph) -> list:
    return sorted((e.source, e.target, e.conditional)
                  for e in graph.get_graph().edges)


def test_a_run_of_k_node_runs_needs_a_limit_of_k_plus_one() -> None:
    for runs in (1, 2, 3, 5, 8):
        graph = loop(stop_at(runs))
        config = {"recursion_limit": runs + 1}
        assert graph.invoke({"count": 0}, config=config)["count"] == runs
        with pytest.raises(GraphRecursionError):
            graph.invoke({"count": 0}, config={"recursion_limit": runs})


def test_the_first_node_runs_in_super_step_one() -> None:
    seen = []

    def note(state: State, config) -> dict:
        seen.append(config["metadata"]["langgraph_step"])
        return add_one(state)

    loop(stop_at(3), note).invoke({"count": 0})
    assert seen == [1, 2, 3]


def test_without_a_literal_the_loop_edge_is_not_drawn() -> None:
    assert edges(loop(plain)) == [
        ("__start__", "add_one", False), ("add_one", "__end__", False)]
    assert edges(loop(stop_at(3))) == [
        ("__start__", "add_one", False), ("add_one", "__end__", True),
        ("add_one", "add_one", True)]
    assert loop(plain).invoke({"count": 0}) == {"count": 3}
