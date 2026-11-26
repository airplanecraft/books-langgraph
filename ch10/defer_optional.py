"""Deferred node: separate edges, a list edge and defer=True when a branch may be skipped.
Book: Chapter 10, section 10.5
Run: python ch10/defer_optional.py
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


# region: optional
def build(kind: str, chosen: list[str]) -> CompiledStateGraph:
    def pick(state: State) -> list[str]:
        return chosen  # ①

    builder = StateGraph(State)
    for label in ("read", "order", "policy", "shipping"):
        builder.add_node(label, make_step(label))
    deferred = kind == "defer"
    builder.add_node("draft", make_step("draft"), defer=deferred)
    builder.add_edge(START, "read")
    builder.add_conditional_edges("read", pick, ["order", "shipping"])  # ②
    builder.add_edge("order", "policy")
    if kind == "list":
        builder.add_edge(["policy", "shipping"], "draft")
    else:
        builder.add_edge("policy", "draft")
        builder.add_edge("shipping", "draft")
    builder.add_edge("draft", END)
    return builder.compile()


for chosen in (["order"], ["order", "shipping"]):
    for kind in ("list", "separate", "defer"):
        graph = build(kind, chosen)
        notes = graph.invoke({"customer": "Ana", "notes": []})["notes"]
        runs = len([note for note in notes if note.startswith("draft")])
        print(chosen, kind, "draft ran", runs, "time(s)")  # ③
# endregion
