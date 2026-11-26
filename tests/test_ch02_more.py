"""More tests for chapter 2: reducer start values, messages and missing keys.
Book: Chapter 2, section 2.6
Run: python -m pytest tests/test_ch02_more.py
"""
import operator
from typing import Annotated, Optional, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


def run(schema: type, node, start: dict) -> dict:
    builder = StateGraph(schema)
    builder.add_node("node", node)
    builder.add_edge(START, "node")
    builder.add_edge("node", END)
    return builder.compile().invoke(start)


class Added(TypedDict):
    notes: Annotated[list[str], operator.add]


def test_a_reducer_key_starts_from_the_empty_value() -> None:
    assert run(Added, lambda s: {"notes": ["b"]}, {}) == {"notes": ["b"]}
    seen = []

    def spy(old: int, new: int) -> int:
        seen.append((old, new))
        return old + new

    class Counted(TypedDict):
        total: Annotated[int, spy]

    run(Counted, lambda state: {"total": 5}, {"total": 2})
    assert seen == [(0, 2), (2, 5)]


def test_an_unbuildable_type_skips_the_first_call() -> None:
    seen = []

    def spy(old: int, new: int) -> int:
        seen.append((old, new))
        return max(old, new)

    class Maybe(TypedDict):
        urgency: Annotated[Optional[int], spy]

    result = run(Maybe, lambda state: {"urgency": 2}, {"urgency": 5})
    assert seen == [(5, 2)] and result == {"urgency": 5}


def test_whole_list_duplicates_and_empty_list_clears_nothing() -> None:
    whole = lambda state: {"notes": state["notes"] + ["x"]}  # noqa: E731
    assert run(Added, whole, {"notes": ["a"]}) == {"notes": ["a", "a", "x"]}
    clear = lambda state: {"notes": []}  # noqa: E731
    assert run(Added, clear, {"notes": ["a"]}) == {"notes": ["a"]}


def test_add_messages_appends_and_replaces() -> None:
    left = [HumanMessage("a", id="1"), AIMessage("b", id="2")]
    right = [AIMessage("c", id="2"), AIMessage("d", id="3")]
    merged = add_messages(left, right)
    assert [(m.id, m.content) for m in merged] == [
        ("1", "a"), ("2", "c"), ("3", "d")]
    made = add_messages([], [{"role": "user", "content": "hi"}])
    assert [m.type for m in made] == ["human"]


def test_a_reducer_is_not_a_node() -> None:
    builder = StateGraph(Added)
    builder.add_node("read", lambda state: {"notes": ["read"]})
    builder.add_edge(START, "read")
    builder.add_edge("read", END)
    nodes = sorted(builder.compile().get_graph().nodes)
    assert nodes == ["__end__", "__start__", "read"]


def test_a_plain_key_left_out_is_missing() -> None:
    class Mixed(TypedDict):
        category: str
        notes: Annotated[list[str], operator.add]

    seen = {}

    def look(state: Mixed) -> dict:
        seen["notes"] = state["notes"]
        seen["has_category"] = "category" in state
        return {}

    run(Mixed, look, {})
    assert seen == {"notes": [], "has_category": False}
