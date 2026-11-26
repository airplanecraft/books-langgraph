"""More tests for chapter 7: what interrupt returns, where a thread waits, and how a resume is matched.
Book: Chapter 7, section 7.2
Run: python -m pytest tests/test_ch07_more.py
"""
from typing import Any, TypedDict

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Interrupt, interrupt

CONFIG = {"configurable": {"thread_id": "t"}}


class State(TypedDict):
    answer: Any


def build(node: Any, checkpointer: Any = "memory") -> Any:
    builder = StateGraph(State)
    builder.add_node("ask", node)
    builder.add_edge(START, "ask")
    builder.add_edge("ask", END)
    saver = InMemorySaver() if checkpointer == "memory" else checkpointer
    return builder.compile(checkpointer=saver)


def ask(state: State) -> dict:
    return {"answer": interrupt("Go on?")}


def test_the_paused_result_holds_an_interrupt_with_the_payload() -> None:
    result = build(ask).invoke({"answer": 0}, CONFIG)
    assert isinstance(result["__interrupt__"][0], Interrupt)
    assert result["__interrupt__"][0].value == "Go on?"
    assert result["answer"] == 0  # the keys that had a value are still there


def test_a_dictionary_payload_comes_back_unchanged() -> None:
    def node(state: State) -> dict:
        return {"answer": interrupt({"question": "Send?", "draft": "Hi"})}

    result = build(node).invoke({"answer": 0}, CONFIG)
    assert result["__interrupt__"][0].value == {"question": "Send?", "draft": "Hi"}


@pytest.mark.parametrize("value", ["yes", False, 0, "", [1, 2], {"a": 1}])
def test_the_resume_value_is_what_interrupt_returns(value: Any) -> None:
    graph = build(ask)
    graph.invoke({"answer": "none"}, CONFIG)
    assert graph.invoke(Command(resume=value), CONFIG)["answer"] == value


def test_the_paused_thread_waits_at_the_node_and_the_finished_one_does_not() -> None:
    graph = build(ask)
    graph.invoke({"answer": 0}, CONFIG)
    snapshot = graph.get_state(CONFIG)
    assert snapshot.next == ("ask",)
    assert snapshot.interrupts[0].value == "Go on?"
    graph.invoke(Command(resume="yes"), CONFIG)
    assert graph.get_state(CONFIG).next == ()


def test_the_pause_saves_no_extra_checkpoint() -> None:
    graph = build(ask)
    graph.invoke({"answer": 0}, CONFIG)
    assert len(list(graph.get_state_history(CONFIG))) == 2
    graph.invoke(Command(resume="yes"), CONFIG)
    assert len(list(graph.get_state_history(CONFIG))) == 3


def test_three_interrupts_take_three_resume_values_in_order() -> None:
    def node(state: State) -> dict:
        first, second, third = (interrupt(n) for n in ("a?", "b?", "c?"))
        return {"answer": [first, second, third]}

    graph = build(node)
    questions = [graph.invoke({"answer": 0}, CONFIG)["__interrupt__"][0].value]
    for value in ("one", "two"):
        result = graph.invoke(Command(resume=value), CONFIG)
        questions.append(result["__interrupt__"][0].value)
    final = graph.invoke(Command(resume="three"), CONFIG)
    assert questions == ["a?", "b?", "c?"]
    assert final["answer"] == ["one", "two", "three"]


def test_resume_without_a_checkpointer_raises_runtime_error() -> None:
    graph = build(ask, checkpointer=None)
    assert "__interrupt__" in graph.invoke({"answer": 0}, CONFIG)
    with pytest.raises(RuntimeError, match="without checkpointer"):
        graph.invoke(Command(resume="yes"), CONFIG)


def test_a_resume_on_an_unused_thread_starts_a_fresh_run_that_pauses() -> None:
    graph = build(ask)
    other = {"configurable": {"thread_id": "other"}}
    result = graph.invoke(Command(resume="yes"), other)
    assert result["__interrupt__"][0].value == "Go on?"
    assert graph.get_state(other).values == {}


def test_a_node_that_catches_exception_swallows_the_pause() -> None:
    def node(state: State) -> dict:
        try:
            answer = interrupt("Go on?")
        except Exception:
            answer = "fallback"
        return {"answer": answer}

    result = build(node).invoke({"answer": 0}, CONFIG)
    assert result == {"answer": "fallback"}
