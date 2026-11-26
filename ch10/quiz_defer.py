"""Self-check run: a list edge and a deferred node when only one branch is chosen.
Book: Chapter 10, section 10.5
Run: python ch10/quiz_defer.py
"""
import operator
from typing import Annotated, Callable, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    log: Annotated[list[str], operator.add]


def make_node(label: str) -> Callable[[State], dict]:
    def node(state: State) -> dict:
        return {"log": [label]}

    return node


def pick(state: State) -> list[str]:
    return ["refund"]


def build(kind: str) -> object:
    builder = StateGraph(State)
    for label in ("triage", "refund", "replace"):
        builder.add_node(label, make_node(label))
    builder.add_node("close", make_node("close"), defer=(kind == "defer"))
    builder.add_edge(START, "triage")
    builder.add_conditional_edges("triage", pick, ["refund", "replace"])
    if kind == "list":
        builder.add_edge(["refund", "replace"], "close")
    else:
        builder.add_edge("refund", "close")
        builder.add_edge("replace", "close")
    builder.add_edge("close", END)
    return builder.compile()


for kind in ("list", "defer"):
    log = build(kind).invoke({"log": []})["log"]
    print(kind, log.count("close"))
