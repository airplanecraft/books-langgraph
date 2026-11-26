"""Self-check run: a Literal routing function with a typo in one branch.
Book: Chapter 3, section 3.6
Run: python ch03/quiz_name.py
"""
# region: name
import operator
from typing import Annotated, Literal, TypedDict
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    score: int
    path: Annotated[list[str], operator.add]


def check(state: State) -> dict:
    return {"path": ["check"]}


def route(state: State) -> Literal["urgent", "routine"]:
    return "urgent" if state["score"] >= 5 else "routin"


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
run = builder.compile().invoke
for score in (7, 2):
    try:
        print("score", score, run({"score": score, "path": []})["path"])
    except KeyError as error:
        print("score", score, "KeyError", error)
# endregion
