"""Self-check run: how many items values and updates give when two nodes write nothing.
Book: Chapter 6, section 6.2
Run: python ch06/quiz_values.py
"""
# region: quiz
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    total: int


def add_one(state: State) -> dict:
    return {"total": state["total"] + 1}


def look(state: State) -> None:
    """Reads the state and changes nothing."""


def nothing_to_say(state: State) -> dict:
    return {}


builder = StateGraph(State)
builder.add_node("a", add_one)
builder.add_node("b", look)
builder.add_node("c", add_one)
builder.add_node("d", nothing_to_say)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", "c")
builder.add_edge("c", "d")
builder.add_edge("d", END)
graph = builder.compile()

start = {"total": 0}
states = list(graph.stream(start, stream_mode="values"))
changes = list(graph.stream(start, stream_mode="updates"))
print(len(states), len(changes))
# endregion
