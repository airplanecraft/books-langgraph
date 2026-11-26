"""Self-check run for chapter 7: where a paused thread stands.
Book: Chapter 7, section 7.2
Run: python ch07/quiz_next.py
"""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class State(TypedDict):
    note: str


def first(state: State) -> dict:
    return {"note": "first ran"}


def second(state: State) -> dict:
    interrupt("Go on?")
    return {"note": "second ran"}


def third(state: State) -> dict:
    return {"note": "third ran"}


builder = StateGraph(State)
builder.add_node("first", first)
builder.add_node("second", second)
builder.add_node("third", third)
builder.add_edge(START, "first")
builder.add_edge("first", "second")
builder.add_edge("second", "third")
builder.add_edge("third", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "q"}}
graph.invoke({"note": ""}, config)
snapshot = graph.get_state(config)
print(snapshot.next, snapshot.values["note"])
