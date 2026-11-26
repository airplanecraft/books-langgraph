"""Show what happens when a node edits the state in place, not by an update.
Book: Chapter 2, section 2.6
Run: python ch02/edit_in_place.py
"""
# region: mutate
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    notes: list[str]
    count: int


def edit_in_place(state: State) -> dict:
    print("your dictionary:", state is start)  # ①
    print("your list:      ", state["notes"] is start["notes"])
    state["notes"].append("edited")  # ②
    state["count"] = 99
    return {}


builder = StateGraph(State)
builder.add_node("edit", edit_in_place)
builder.add_edge(START, "edit")
builder.add_edge("edit", END)

start = {"notes": ["received"], "count": 0}
print("result:    ", builder.compile().invoke(start))
print("your input:", start)
# endregion
