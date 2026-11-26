"""Tests for chapter 4: exercise solutions and what the tool node does.
Book: Chapter 4, section 4.8
Run: python -m pytest tests/test_ch04.py
"""
import subprocess
import sys
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage
from langchain_core.tools import ToolException
from langgraph.prebuilt import ToolNode

from ch04_helpers import (lookup_order, raises_tool_exception,
                          raises_validation_error, raises_value_error, request,
                          tool_node_graph)

ROOT = Path(__file__).parent.parent

SOLUTIONS = {
    "solutions/ch04_ex1.py":
        "model node receives 1 ['human']\n"
        "model node receives 4 ['human', 'ai', 'tool', 'tool']\n"
        "final 5 ['human', 'ai', 'tool', 'tool', 'ai']",
    "solutions/ch04_ex2.py": "$35.50\nThe total is $35.50.",
    "solutions/ch04_ex3.py": "payment service is down, try later\n4",
}


@pytest.mark.parametrize("script", SOLUTIONS)
def test_solution_prints_what_the_exercise_asks_for(script: str) -> None:
    result = subprocess.run([sys.executable, script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == SOLUTIONS[script]


def test_tool_node_answers_every_call_in_request_order() -> None:
    calls = [{"name": "lookup_order", "args": {"order_id": "A17"}, "id": "c1"},
             {"name": "lookup_order", "args": {"order_id": "B42"}, "id": "c2"}]
    state = {"messages": [AIMessage(content="", tool_calls=calls)]}
    messages = tool_node_graph([lookup_order]).invoke(state)["messages"]
    assert [(m.tool_call_id, m.content) for m in messages[1:]] == [
        ("c1", "shipped on 18 November"), ("c2", "delayed: waiting for stock")]


def test_a_tool_node_cannot_run_outside_a_graph() -> None:
    state = {"messages": [request("lookup_order", {"order_id": "A17"})]}
    with pytest.raises(ValueError):
        ToolNode([lookup_order]).invoke(state)


def test_bad_arguments_and_unknown_names_become_tool_messages() -> None:
    graph = tool_node_graph([lookup_order])
    for ask in (request("lookup_order", {"order_id": 42}),
                request("lookup_order", {}),
                request("cancel_order", {"order_id": "B42"})):
        last = graph.invoke({"messages": [ask]})["messages"][-1]
        assert last.type == "tool" and last.status == "error"
    unknown = graph.invoke({"messages": [request("cancel_order", {})]})
    assert "is not a valid tool" in unknown["messages"][-1].content


@pytest.mark.parametrize("tool, error", [
    (raises_value_error, ValueError), (raises_tool_exception, ToolException)])
def test_an_exception_inside_a_tool_stops_the_run(tool, error) -> None:
    graph = tool_node_graph([tool])
    ask = request(tool.name, {"order_id": "B42"})
    with pytest.raises(error):
        graph.invoke({"messages": [ask]})


def test_a_validation_error_raised_inside_a_tool_body_is_a_tool_message() -> None:
    graph = tool_node_graph([raises_validation_error])
    ask = request("raises_validation_error", {"order_id": "B42"})
    assert graph.invoke({"messages": [ask]})["messages"][-1].status == "error"
