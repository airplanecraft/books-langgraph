"""More tests for chapter 9: the rules behind the listings, found by probes.
Book: Chapter 9, section 9.4
Run: python -m pytest tests/test_ch09_more.py
"""
import operator
import warnings
from typing import Annotated, TypedDict

import pytest
from langgraph._internal._retry import default_retry_on
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import EmptyInputError, GraphRecursionError, NodeError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, RetryPolicy

FAST = {"initial_interval": 0.01, "jitter": False}


class State(TypedDict):
    notes: Annotated[list, operator.add]


def one_node_graph(error: Exception, runs: list, **node_options: object):
    def node(state: State) -> dict:
        runs.append("run")
        raise error

    builder = StateGraph(State)
    builder.add_node("node", node, **node_options)
    builder.add_edge(START, "node")
    return builder.compile()


@pytest.mark.parametrize("error, retried", [
    (ConnectionError(), True), (ConnectionResetError(), True),
    (TimeoutError(), False), (OSError(), False), (FileNotFoundError(), False),
    (ValueError(), False), (TypeError(), False), (KeyError(), False),
    (RuntimeError(), False), (NotImplementedError(), False),
    (ZeroDivisionError(), False), (AssertionError(), True), (Exception(), True),
])
def test_default_retry_on(error: Exception, retried: bool) -> None:
    assert default_retry_on(error) is retried


def test_retry_on_replaces_the_default() -> None:
    runs: list = []
    policy = RetryPolicy(retry_on=ValueError, **FAST)
    with pytest.raises(ConnectionError):
        one_node_graph(ConnectionError("x"), runs, retry_policy=policy).invoke({"notes": []})
    assert len(runs) == 1


def test_recursion_limit_error_is_not_retried() -> None:
    runs: list = []

    def loop(state: State) -> dict:
        runs.append("run")
        return {}

    builder = StateGraph(State)
    builder.add_node("loop", loop, retry_policy=RetryPolicy(retry_on=Exception, **FAST))
    builder.add_edge(START, "loop")
    builder.add_conditional_edges("loop", lambda state: "loop", ["loop"])
    with pytest.raises(GraphRecursionError):
        builder.compile().invoke({"notes": []}, {"recursion_limit": 4})
    assert len(runs) == 4


def test_a_handler_runs_for_an_exception_that_is_not_retried() -> None:
    def handler(state: State, error: NodeError) -> Command:
        return Command(update={"notes": [type(error.error).__name__]})

    runs: list = []
    graph = one_node_graph(ValueError("x"), runs, retry_policy=RetryPolicy(**FAST),
                           error_handler=handler)
    assert graph.invoke({"notes": []})["notes"] == ["ValueError"] and len(runs) == 1


def test_none_on_a_new_thread_raises_and_durability_needs_a_checkpointer() -> None:
    builder = StateGraph(State)
    builder.add_node("a", lambda state: {})
    builder.add_edge(START, "a")
    builder.add_edge("a", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    with pytest.raises(EmptyInputError):
        graph.invoke(None, {"configurable": {"thread_id": "new"}})
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        builder.compile().invoke({"notes": []}, durability="exit")
    assert "no effect" in str(caught[0].message)
