"""A reducer lets two parallel nodes write one key; the notes come out in name order in these runs.
Book: Chapter 10, section 10.3
Run: python ch10/merge_order.py
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


# region: merge
def build(first: str, second: str) -> CompiledStateGraph:
    builder = StateGraph(State)
    for label in ("read", "draft", first, second):  # ①
        builder.add_node(label, make_step(label))
    builder.add_edge(START, "read")
    for label in (first, second):
        builder.add_edge("read", label)
        builder.add_edge(label, "draft")
    builder.add_edge("draft", END)
    return builder.compile()


for names in (("plan", "order"), ("order", "plan")):
    result = build(*names).invoke({"customer": "Ana", "notes": []})
    print(names, [note.split(":")[0] for note in result["notes"]])  # ②
# endregion
