"""Helpers for the chapter 5 tests: the ticket graph with a checkpointer, and a chain of n nodes.
Book: Chapter 5, section 5.3
Run: python -m pytest tests/test_ch05.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class Ticket(TypedDict):
    customer: str
    notes: Annotated[list, operator.add]


def read(state: Ticket) -> dict:
    return {"notes": ["read the email"]}


def draft(state: Ticket) -> dict:
    return {"notes": ["wrote a reply"]}


def ticket_builder() -> StateGraph:
    builder = StateGraph(Ticket)
    builder.add_node("read", read)
    builder.add_node("draft", draft)
    builder.add_edge(START, "read")
    builder.add_edge("read", "draft")
    builder.add_edge("draft", END)
    return builder


def ticket_graph():
    return ticket_builder().compile(checkpointer=InMemorySaver())


def thread(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def chain_graph(length: int):
    """A graph of `length` nodes in a row, with a checkpointer."""
    builder = StateGraph(Ticket)
    names = [f"n{index}" for index in range(length)]
    for name in names:
        builder.add_node(name, lambda state: {"notes": ["x"]})
    builder.add_edge(START, names[0])
    for left, right in zip(names, names[1:]):
        builder.add_edge(left, right)
    builder.add_edge(names[-1], END)
    return builder.compile(checkpointer=InMemorySaver())
