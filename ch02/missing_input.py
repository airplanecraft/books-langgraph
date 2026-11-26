"""Show a node reading a key the input left out: plain keys are missing.
Book: Chapter 2, section 2.6
Run: python ch02/missing_input.py
"""
# region: missing
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    category: str
    notes: Annotated[list[str], operator.add]


def look(state: State) -> dict:
    print("notes:", state["notes"])  # ①
    try:
        print("category:", state["category"])  # ②
    except KeyError as error:
        print("category: KeyError", error)
    print("with get:", state.get("category", "not set"))  # ③
    return {}


builder = StateGraph(State)
builder.add_node("look", look)
builder.add_edge(START, "look")
builder.add_edge("look", END)
builder.compile().invoke({"customer": "Ana"})
# endregion
