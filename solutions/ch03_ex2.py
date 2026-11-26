"""Exercise 3.2: a review loop that gives up after three drafts.
Book: Chapter 3, section 3.2
Run: python solutions/ch03_ex2.py
"""
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    drafts: int
    approved: bool


def draft(state: State) -> dict:
    return {"drafts": state["drafts"] + 1}


def review(state: State) -> dict:
    return {"approved": False}  # this review never approves


def after_review(state: State) -> Literal["draft", "__end__"]:
    if state["approved"] or state["drafts"] >= 3:
        return END
    return "draft"


builder = StateGraph(State)
builder.add_node("draft", draft)
builder.add_node("review", review)
builder.add_edge(START, "draft")
builder.add_edge("draft", "review")
builder.add_conditional_edges("review", after_review)
result = builder.compile().invoke({"drafts": 0, "approved": False})
print(result["drafts"], result["approved"])
