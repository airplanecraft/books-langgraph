"""Deferred node: defer=True waits for every pending branch, also one that does not lead to it.
Book: Chapter 10, section 10.5
Run: python ch10/defer_waits.py
"""
import operator
from typing import Annotated, Callable, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph


class State(TypedDict):
    customer: str
    notes: Annotated[list[str], operator.add]


def make_step(label: str) -> Callable[[State, RunnableConfig], dict]:
    def step(state: State, config: RunnableConfig) -> dict:
        number = config["metadata"]["langgraph_step"]
        seen = len(state["notes"])
        note = f"{label}: super-step {number}, notes seen {seen}"
        return {"notes": [note]}

    return step


# region: waits
def build(kind: str) -> CompiledStateGraph:
    builder = StateGraph(State)
    for label in ("read", "order", "shipping", "audit_1", "audit_2"):
        builder.add_node(label, make_step(label))
    deferred = kind == "defer"
    builder.add_node("draft", make_step("draft"), defer=deferred)
    builder.add_edge(START, "read")
    for label in ("order", "shipping", "audit_1"):
        builder.add_edge("read", label)
    builder.add_edge("audit_1", "audit_2")  # ①
    builder.add_edge("audit_2", END)
    if kind == "list":
        builder.add_edge(["order", "shipping"], "draft")
    else:
        builder.add_edge("order", "draft")
        builder.add_edge("shipping", "draft")
    builder.add_edge("draft", END)
    return builder.compile()


for kind in ("list", "defer"):
    notes = build(kind).invoke({"customer": "Ana", "notes": []})["notes"]
    print(kind)
    for note in notes:
        if note.startswith(("audit_2", "draft")):  # ②
            print("  ", note)
# endregion
