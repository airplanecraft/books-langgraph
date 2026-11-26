"""Tests for chapter 0: exercise solutions and the facts the chapter states.
Book: Chapter 0, section 0.6
Run: python -m pytest tests/test_ch00.py
"""
import subprocess
import sys
from pathlib import Path

import pytest
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from common import ScriptedModel, ask_for, say

ROOT = Path(__file__).parent.parent

SOLUTIONS = {
    "solutions/ch00_ex1.py": "['human', 'ai', 'tool']",
    "solutions/ch00_ex2.py": "tool: estimate_delivery -> expected 22 November\n"
                             "answer: Order A17 should arrive on 22 November.",
    "solutions/ch00_ex3.py": "round: Order A17 shipped on 18 November.\ndirect: Hello!",
}


@pytest.mark.parametrize("script", SOLUTIONS)
def test_solution_prints_what_the_exercise_asks_for(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == SOLUTIONS[script]


def test_tool_shows_name_description_and_parameters() -> None:
    @tool
    def lookup_order(order_id: str) -> str:
        """Look up the shipping status of an order by its ID, such as A17."""
        return "x"

    assert lookup_order.name == "lookup_order"
    assert lookup_order.description.startswith("Look up the shipping")
    assert list(lookup_order.args) == ["order_id"]


def test_message_ids_start_empty_and_can_be_chosen() -> None:
    assert HumanMessage("Hi").id is None
    assert HumanMessage("Hi", id="h1").id == "h1"


def test_tool_message_needs_a_tool_call_id() -> None:
    with pytest.raises(Exception):
        ToolMessage(content="x")


def test_scripted_reply_without_tool_has_empty_tool_calls() -> None:
    model = ScriptedModel(script=[say("Hi"), ask_for("lookup_order", {"order_id": "A17"})])
    assert model.invoke("x").tool_calls == []
    assert model.invoke("x").tool_calls[0]["name"] == "lookup_order"


def test_dictionary_and_object_forms_are_both_accepted() -> None:
    model = ScriptedModel(script=[say("a"), say("b")])
    assert model.invoke([{"role": "user", "content": "x"}]).content == "a"
    assert model.invoke([HumanMessage("x")]).content == "b"
