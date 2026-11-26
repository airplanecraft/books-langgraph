"""Fan-in: separate edges, a list edge and defer=True compared on branches of unequal length.
Book: Chapter 10, section 10.4
Run: python ch10/fan_in.py
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


# region: join
def build(kind: str) -> CompiledStateGraph:
    builder = StateGraph(State)
    for label in ("read", "order", "policy", "shipping"):
        builder.add_node(label, make_step(label))
    deferred = kind == "defer"
    builder.add_node("draft", make_step("draft"), defer=deferred)  # ①
    builder.add_edge(START, "read")
    builder.add_edge("read", "order")
    builder.add_edge("order", "policy")  # ②
    builder.add_edge("read", "shipping")
    if kind == "list":
        builder.add_edge(["policy", "shipping"], "draft")  # ③
    else:
        builder.add_edge("policy", "draft")
        builder.add_edge("shipping", "draft")
    builder.add_edge("draft", END)
    return builder.compile()


for kind in ("separate", "list", "defer"):
    notes = build(kind).invoke({"customer": "Ana", "notes": []})["notes"]
    print(kind)
    for note in notes:
        if note.startswith("draft"):
            print("  ", note)  # ④
# endregion
