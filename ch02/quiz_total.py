"""Self-check run: an integer key with operator.add, an input, and two updates.
Book: Chapter 2, section 2.3
Run: python ch02/quiz_total.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


# region: total
class State(TypedDict):
    total: Annotated[int, operator.add]


def first(state: State) -> dict:
    return {"total": 5}


def second(state: State) -> dict:
    return {"total": -2}


builder = StateGraph(State)
builder.add_node("first", first)
builder.add_node("second", second)
builder.add_edge(START, "first")
builder.add_edge("first", "second")
builder.add_edge("second", END)
print(builder.compile().invoke({"total": 10}))
# endregion
