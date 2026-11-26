"""More tests for chapter 3: drawn edges and wrong node names.
Book: Chapter 3, section 3.6
Run: python -m pytest tests/test_ch03_more.py
"""
from typing import Literal, TypedDict, get_args, get_type_hints

import pytest
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    count: int


def add_one(state: State) -> dict:
    return {"count": state["count"] + 1}


def loop(route) -> object:
    builder = StateGraph(State)
    builder.add_node("add_one", add_one)
    builder.add_edge(START, "add_one")
    builder.add_conditional_edges("add_one", route)
    return builder.compile()


def edges(graph) -> list:
    return sorted((e.source, e.target, e.conditional)
                  for e in graph.get_graph().edges)


def test_a_command_return_type_draws_the_edges() -> None:
    def hinted(state: State) -> Command[Literal["add_one", "__end__"]]:
        return Command(goto=END)

    def bare(state: State):
        return Command(goto=END)

    for node, drawn in ((hinted, True), (bare, False)):
        builder = StateGraph(State)
        builder.add_node("first", node)
        builder.add_node("add_one", add_one)
        builder.add_edge(START, "first")
        builder.add_edge("add_one", END)
        found = ("first", "add_one", True) in edges(builder.compile())
        assert found == drawn


def test_a_wrong_name_ends_quietly_unless_there_is_a_literal() -> None:
    def wrong_literal(state: State) -> Literal["add_one"]:
        return "no_such_node"  # type: ignore[return-value]

    assert loop(lambda state: "no_such_node").invoke({"count": 0}) == {
        "count": 1}
    with pytest.raises(KeyError):
        loop(wrong_literal).invoke({"count": 0})


def test_a_goto_name_can_be_checked_against_the_return_type() -> None:
    def node(state: State) -> Command[Literal["add_one", "__end__"]]:
        return Command(goto="add_on")

    hint = get_type_hints(node)["return"]
    allowed = get_args(get_args(hint)[0])
    assert node({"count": 0}).goto not in allowed
    assert "add_one" in allowed
