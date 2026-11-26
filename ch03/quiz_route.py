"""Self-check run: a routing function that compares a score with 5.
Book: Chapter 3, section 3.1
Run: python ch03/quiz_route.py
"""
# region: route
import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    score: int
    path: Annotated[list[str], operator.add]


def check(state: State) -> dict:
    return {"path": ["check"]}


def route(state: State) -> Literal["urgent", "routine"]:
    return "urgent" if state["score"] >= 5 else "routine"


def urgent(state: State) -> dict:
    return {"path": ["urgent"]}


def routine(state: State) -> dict:
    return {"path": ["routine"]}


builder = StateGraph(State)
builder.add_node("check", check)
builder.add_node("urgent", urgent)
builder.add_node("routine", routine)
builder.add_edge(START, "check")
builder.add_conditional_edges("check", route)
builder.add_edge("urgent", END)
builder.add_edge("routine", END)
print(builder.compile().invoke({"score": 5, "path": []})["path"])
# endregion
