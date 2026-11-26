"""Show two mistakes with a reducer key, and Overwrite to clear one.
Book: Chapter 2, section 2.6
Run: python ch02/pitfalls.py
"""
# region: duplicate
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Overwrite


class State(TypedDict):
    notes: Annotated[list[str], operator.add]


def whole_list(state: State) -> dict:
    return {"notes": state["notes"] + ["drafted"]}  # ①


def only_new(state: State) -> dict:
    return {"notes": ["drafted"]}  # ②


def clear(state: State) -> dict:
    return {"notes": []}  # ③


def clear_all(state: State) -> dict:
    return {"notes": Overwrite([])}  # ④


for node in (whole_list, only_new, clear, clear_all):
    builder = StateGraph(State)
    builder.add_node("node", node)
    builder.add_edge(START, "node")
    builder.add_edge("node", END)
    print(node.__name__, builder.compile().invoke({"notes": ["received"]}))
# endregion
