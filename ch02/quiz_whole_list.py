"""Self-check run: a node returns the old list plus a note, with no reducer.
Book: Chapter 2, section 2.2
Run: python ch02/quiz_whole_list.py
"""
# region: whole
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    notes: list[str]


def draft(state: State) -> dict:
    return {"notes": state["notes"] + ["drafted"]}


builder = StateGraph(State)
builder.add_node("draft", draft)
builder.add_edge(START, "draft")
builder.add_edge("draft", END)
print(builder.compile().invoke({"notes": ["received"]}))
# endregion
