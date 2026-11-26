"""More tests for chapter 12: store behaviour, context and the pitfalls.
Book: Chapter 12, section 12.8
Run: python -m pytest tests/test_ch12_more.py
"""
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypedDict

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore


@dataclass
class Context:
    user_id: str


class State(TypedDict, total=False):
    seen: str


def build(node: Callable, **compile_args: object) -> CompiledStateGraph:
    builder = StateGraph(State, context_schema=Context)
    builder.add_node("node", node)
    builder.add_edge(START, "node")
    builder.add_edge("node", END)
    return builder.compile(**compile_args)


def test_put_get_search_and_misses() -> None:
    store = InMemoryStore()
    store.put(("a", "b"), "k", {"n": 1})
    assert store.get(("a", "b"), "k").value == {"n": 1}
    assert store.get(("a", "c"), "k") is None
    assert store.get(("a",), "k") is None
    assert [i.key for i in store.search(("a",))] == ["k"]
    assert store.search(("a", "c")) == []
    assert InMemoryStore().get(("a", "b"), "k") is None


def test_search_filter_and_query_without_index() -> None:
    store = InMemoryStore()
    store.put(("u", "x"), "one", {"tone": "short"})
    store.put(("u", "x"), "two", {"tone": "long"})
    assert [i.key for i in store.search(("u",), filter={"tone": "long"})] == [
        "two"]
    found = store.search(("u", "x"), query="anything")
    assert [(i.key, i.score) for i in found] == [("one", None), ("two", None)]


def test_runtime_store_and_context_reach_the_node() -> None:
    seen = []

    def node(state: State, runtime: Runtime[Context]) -> dict:
        seen.append((runtime.context, runtime.store))
        return {}

    store = InMemoryStore()
    build(node, store=store).invoke({}, context={"user_id": "ana"})
    assert seen == [(Context("ana"), store)]


def test_context_is_not_saved_with_the_thread() -> None:
    def node(state: State, runtime: Runtime[Context]) -> dict:
        return {"seen": str(runtime.context)}

    graph = build(node, checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "t"}}
    graph.invoke({}, config, context=Context("ana"))
    snapshot = graph.get_state(config)
    assert "ana" not in str(snapshot.config) + str(snapshot.metadata)
    assert graph.invoke({}, config) == {"seen": "None"}


def test_configurable_values_are_not_the_context() -> None:
    seen = []

    def node(state: State, runtime: Runtime[Context]) -> dict:
        seen.append(runtime.context)
        return {}

    build(node).invoke({}, {"configurable": {"user_id": "ana"}})
    assert seen == [None]


def test_missing_store_is_none_and_bad_context_keys_raise() -> None:
    def node(state: State, runtime: Runtime[Context]) -> dict:
        assert runtime.store is None
        return {}

    graph = build(node)
    graph.invoke({}, context=Context("ana"))
    with pytest.raises(TypeError):
        graph.invoke({}, context={"nope": 1})

