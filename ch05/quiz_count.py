"""Self-check run: how many checkpoints a chain of three nodes leaves.
Book: Chapter 5, section 5.3
Run: python ch05/quiz_count.py
"""
# region: quiz
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str


def first(state: State) -> dict:
    return {}


def second(state: State) -> dict:
    return {}


def third(state: State) -> dict:
    return {}


builder = StateGraph(State)
builder.add_node("first", first)
builder.add_node("second", second)
builder.add_node("third", third)
builder.add_edge(START, "first")
builder.add_edge("first", "second")
builder.add_edge("second", "third")
builder.add_edge("third", END)
graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "t1"}}
graph.invoke({"customer": "Ana"}, config)
print(len(list(graph.get_state_history(config))), "checkpoints")
# endregion
