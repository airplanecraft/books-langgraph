"""Show that a type with no empty value skips the reducer for its first value.
Book: Chapter 2, section 2.3
Run: python ch02/first_value.py
"""
# region: first
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


def keep_max(old: int, new: int) -> int:
    print(f"keep_max(old={old}, new={new})")
    return max(old, new)


class State(TypedDict):
    urgency: Annotated[int | None, keep_max]  # ①


def draft(state: State) -> dict:
    return {"urgency": 2}


builder = StateGraph(State)
builder.add_node("draft", draft)
builder.add_edge(START, "draft")
builder.add_edge("draft", END)
print(builder.compile().invoke({"urgency": 5}))
# endregion
