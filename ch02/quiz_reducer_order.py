"""Self-check run: a reducer that puts the new text before the old text.
Book: Chapter 2, section 2.3
Run: python ch02/quiz_reducer_order.py
"""
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


# region: order
def newest_first(old: str, new: str) -> str:
    return new + old


class State(TypedDict):
    log: Annotated[str, newest_first]


def one(state: State) -> dict:
    return {"log": "B"}


def two(state: State) -> dict:
    return {"log": "C"}


builder = StateGraph(State)
builder.add_node("one", one)
builder.add_node("two", two)
builder.add_edge(START, "one")
builder.add_edge("one", "two")
builder.add_edge("two", END)
print(builder.compile().invoke({"log": "A"}))
# endregion
