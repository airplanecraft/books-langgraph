"""The recursion limit of the fan-out graph: five node runs, three super-steps.
Book: Chapter 10, section 10.2
Run: python ch10/parallel_limit.py
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


builder = StateGraph(State)
for label in ("read", "order", "plan", "shipping", "draft"):
    builder.add_node(label, make_step(label))
builder.add_edge(START, "read")
for label in ("order", "plan", "shipping"):
    builder.add_edge("read", label)
    builder.add_edge(label, "draft")
builder.add_edge("draft", END)
graph: CompiledStateGraph = builder.compile()

# region: limit
from langgraph.errors import GraphRecursionError

for limit in (3, 4):
    try:
        graph.invoke({"customer": "Ana", "notes": []},
                     config={"recursion_limit": limit})
        print("limit", limit, "finished")  # ①
    except GraphRecursionError:
        print("limit", limit, "GraphRecursionError")  # ②
# endregion
