"""Tests for chapter 12: store parameter, search limit, mutable and frozen context.
Book: Chapter 12, section 12.6
Run: python -m pytest tests/test_ch12_extra.py
"""
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore


class State(TypedDict, total=False):
    seen: str


@dataclass
class Plain:
    user_id: str


def build(first: Callable, second: Callable | None = None,
          **compile_args: object) -> CompiledStateGraph:
    builder = StateGraph(State, context_schema=Plain)
    builder.add_node("first", first)
    builder.add_edge(START, "first")
    last = "first"
    if second:
        builder.add_node("second", second)
        builder.add_edge("first", "second")
        last = "second"
    builder.add_edge(last, END)
    return builder.compile(**compile_args)


def test_store_parameter_reaches_the_store() -> None:
    seen = []

    def node(state: State, store: BaseStore) -> dict:
        seen.append(store)
        return {}

    store = InMemoryStore()
    build(node, store=store).invoke({})
    assert seen == [store]


def test_search_returns_ten_items_unless_limit_is_given() -> None:
    store = InMemoryStore()
    for number in range(12):
        store.put(("log",), f"k{number}", {"n": number})
    assert len(store.search(("log",))) == 10
    assert len(store.search(("log",), limit=100)) == 12


def test_a_node_can_change_a_plain_context_for_the_next_node() -> None:
    def first(state: State, runtime: Runtime[Plain]) -> dict:
        runtime.context.user_id = "changed"
        return {}

    def second(state: State, runtime: Runtime[Plain]) -> dict:
        return {"seen": runtime.context.user_id}

    assert build(first, second).invoke({}, context=Plain("a")) == {
        "seen": "changed"}


def test_a_string_namespace_is_accepted_and_not_found_as_a_tuple() -> None:
    store = InMemoryStore()
    store.put("users", "k", {"n": 1})
    assert store.get(("users",), "k") is None
    assert store.get("users", "k").namespace == ("u", "s", "e", "r", "s")
