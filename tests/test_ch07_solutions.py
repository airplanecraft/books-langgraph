"""Tests for chapter 7: the self-check runs and the exercise solutions print what the book says.
Book: Chapter 7, section 7.4
Run: python -m pytest tests/test_ch07_solutions.py
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

OUTPUTS = {
    "ch07/quiz_next.py": "('second',) first ran",
    "ch07/quiz_value.py": "{'price': 4, 'total': 12}",
    "ch07/quiz_prepare.py": "['look_up', 'confirm', 'confirm']",
    "ch07/quiz_two.py": "['got x', 'got x', 'got y']",
    "solutions/ch07_ex1.py": (
        "announce runs\n"
        "asked: Which order?\n"
        "first answer: B42\n"
        "asked: Which reason?\n"
        "first answer: B42\n"
        "second answer: late\n"
        "final: ['B42', 'late']"),
    "solutions/ch07_ex2.py": "t5 -> escalated | Hi Ana, B42 is delayed.",
    "solutions/ch07_ex3.py": (
        "A17 tool message: refund sent for A17 (20)\n"
        "B42 asked: Refund 250 for order B42?\n"
        "B42 tool message: refund sent for B42 (250)"),
}


@pytest.mark.parametrize("script", OUTPUTS)
def test_script_prints_what_the_book_shows(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == OUTPUTS[script]


def test_a_resume_with_none_raises_and_the_thread_stays_paused() -> None:
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import END, START, StateGraph
    from langgraph.types import Command, interrupt
    from typing import TypedDict

    class State(TypedDict):
        status: str

    def review(state: State) -> dict:
        return {"status": interrupt("Go on?")}

    builder = StateGraph(State)
    builder.add_node("review", review)
    builder.add_edge(START, "review")
    builder.add_edge("review", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "t"}}
    graph.invoke({"status": "new"}, config)
    with pytest.raises(UnboundLocalError):
        graph.invoke(Command(resume=None), config)
    assert graph.get_state(config).next == ("review",)
    other = {"configurable": {"thread_id": "t", "user": "someone else"}}
    assert graph.invoke(Command(resume="yes"), other)["status"] == "yes"
