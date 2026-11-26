"""Self-check run: update_state on an older copy with a reducer key and as_node.
Book: Chapter 8, section 8.5
Run: python ch08/quiz_fork.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    items: Annotated[list, operator.add]
    status: str


def one(state: State) -> dict:
    return {"items": ["a"], "status": "one"}


def two(state: State) -> dict:
    return {"items": ["b"], "status": "two"}


def three(state: State) -> dict:
    return {"items": ["c"], "status": "three"}


builder = StateGraph(State)
builder.add_node("one", one)
builder.add_node("two", two)
builder.add_node("three", three)
builder.add_edge(START, "one")
builder.add_edge("one", "two")
builder.add_edge("two", "three")
builder.add_edge("three", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "q2"}}
graph.invoke({"items": [], "status": ""}, config)
before_two = next(snapshot for snapshot in graph.get_state_history(config)
                  if snapshot.next == ("two",))
update = {"items": ["x"], "status": "edited"}
fork = graph.update_state(before_two.config, update)
print(graph.get_state(fork).values, graph.get_state(fork).next)
skip = graph.update_state(before_two.config, update, as_node="two")
print(graph.get_state(skip).next)
print(graph.invoke(None, skip)["items"])
