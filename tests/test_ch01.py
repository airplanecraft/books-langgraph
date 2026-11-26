"""Tests for chapter 1: exercise solutions and the facts the chapter states.
Book: Chapter 1, section 1.7
Run: python -m pytest tests/test_ch01.py
"""
import subprocess
import sys
from pathlib import Path
from typing import TypedDict

import pytest
from langgraph.graph import END, START, StateGraph

ROOT = Path(__file__).parent.parent

SOLUTIONS = {
    "solutions/ch01_ex1.py":
        "shipping\nHi Ben, we are checking your shipping question.",
    "solutions/ch01_ex2.py":
        "Hi Ana, we are checking your billing question. -- Support team",
}


@pytest.mark.parametrize("script", SOLUTIONS)
def test_solution_prints_what_the_exercise_asks_for(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == SOLUTIONS[script]


def test_exercise_3_prints_body_category_and_four_edges() -> None:
    result = subprocess.run([sys.executable, "solutions/ch01_ex3.py"], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    body, category, edges = result.stdout.strip().splitlines()
    assert body == "i was charged twice."
    assert category == "billing"
    assert sorted(eval(edges)) == sorted([
        ("__start__", "clean"), ("clean", "classify"),
        ("classify", "draft"), ("draft", "__end__")])


class State(TypedDict):
    customer: str
    body: str
    category: str
    reply: str


def classify(state: State) -> dict:
    category = "billing" if "charged" in state["body"] else "other"
    return {"category": category}


def draft(state: State) -> dict:
    name, topic = state["customer"], state["category"]
    return {"reply": f"Hi {name}, we are checking your {topic} question."}


def build() -> StateGraph:
    builder = StateGraph(State)
    builder.add_node("classify", classify)
    builder.add_node("draft", draft)
    builder.add_edge(START, "classify")
    builder.add_edge("classify", "draft")
    builder.add_edge("draft", END)
    return builder


TICKET = {"customer": "Ana", "body": "I was charged twice for May.",
          "category": "unknown", "reply": ""}


def test_a_typed_dict_ticket_is_a_plain_dict() -> None:
    ticket: State = dict(TICKET)  # type: ignore[assignment]
    assert type(ticket) is dict


def test_graph_returns_the_state_the_hand_run_builds() -> None:
    by_hand = dict(TICKET)
    by_hand.update(classify(by_hand))
    by_hand.update(draft(by_hand))
    assert build().compile().invoke(dict(TICKET)) == by_hand


def test_keys_a_node_does_not_return_keep_their_values() -> None:
    result = build().compile().invoke(dict(TICKET))
    assert result["customer"] == "Ana"
    assert result["body"] == TICKET["body"]


def test_add_node_order_does_not_decide_the_run_order() -> None:
    log: list[str] = []

    def make(name: str):
        def node(state: State) -> dict:
            log.append(name)
            return {}
        return node

    builder = StateGraph(State)
    builder.add_node("second", make("second"))
    builder.add_node("first", make("first"))
    builder.add_edge(START, "first")
    builder.add_edge("first", "second")
    builder.add_edge("second", END)
    builder.compile().invoke(dict(TICKET))
    assert log == ["first", "second"]
