"""Tests for chapter 5: the snapshot, the mistakes and the in-memory limit.
Book: Chapter 5, section 5.6
Run: python -m pytest tests/test_ch05_errors.py
"""
import pytest
from langgraph.checkpoint.memory import InMemorySaver

from ch05_helpers import thread, ticket_builder, ticket_graph

START_INPUT = {"customer": "Ana", "notes": []}


def test_get_state_of_an_unused_thread_is_empty() -> None:
    saved = ticket_graph().get_state(thread("nobody"))
    assert saved.values == {} and saved.metadata is None and saved.next == ()
    assert saved.config == thread("nobody")


def test_a_snapshot_has_these_fields() -> None:
    graph = ticket_graph()
    graph.invoke(START_INPUT, thread("t"))
    fields = type(graph.get_state(thread("t")))._fields
    assert fields == ("values", "next", "config", "metadata", "created_at",
                      "parent_config", "tasks", "interrupts")
    assert sorted(graph.get_state(thread("t")).config["configurable"]) == [
        "checkpoint_id", "checkpoint_ns", "thread_id"]


def test_missing_thread_id_and_missing_checkpointer() -> None:
    graph = ticket_graph()
    with pytest.raises(ValueError, match="Checkpointer requires"):
        graph.invoke(START_INPUT)
    with pytest.raises(ValueError, match="Checkpointer requires"):
        graph.invoke(START_INPUT, {"recursion_limit": 5})
    with pytest.raises(KeyError):
        graph.invoke(START_INPUT, {"configurable": {"user": "ana"}})
    plain = ticket_builder().compile()
    plain.invoke(START_INPUT, thread("t"))
    assert plain.invoke({"notes": ["b"]}, thread("t"))["notes"][0] == "b"
    with pytest.raises(ValueError, match="No checkpointer set"):
        plain.get_state(thread("t"))


def test_a_new_saver_knows_nothing_of_an_old_one() -> None:
    first = ticket_builder().compile(checkpointer=InMemorySaver())
    first.invoke(START_INPUT, thread("t"))
    second = ticket_builder().compile(checkpointer=InMemorySaver())
    assert list(first.get_state_history(thread("t"))) != []
    assert list(second.get_state_history(thread("t"))) == []


def test_a_chat_thread_keeps_one_copy_per_super_step_and_invoke() -> None:
    from langgraph.graph import END, START, MessagesState, StateGraph

    builder = StateGraph(MessagesState)
    builder.add_node("chat", lambda state: {"messages": [("ai", "hi")]})
    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    for thread_id in ["ana", "ana", "ben"]:
        graph.invoke({"messages": [("user", "hello")]}, thread(thread_id))
    assert len(list(graph.get_state_history(thread("ana")))) == 6
    assert len(list(graph.get_state_history(thread("ben")))) == 3
