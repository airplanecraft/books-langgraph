"""A frozen context: Python refuses a node that tries to change it.
Book: Chapter 12, section 12.6
Run: python ch12/context_frozen.py
"""
# region: frozen
from dataclasses import FrozenInstanceError, dataclass
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime


@dataclass(frozen=True)
class Context:
    user_id: str


class State(TypedDict, total=False):
    greeting: str


def greet(state: State, runtime: Runtime[Context]) -> dict:
    try:
        runtime.context.user_id = "ben"  # ①
    except FrozenInstanceError as error:
        print("refused:", error)
    return {"greeting": f"Hello, {runtime.context.user_id}."}


builder = StateGraph(State, context_schema=Context)
builder.add_node("greet", greet)
builder.add_edge(START, "greet")
builder.add_edge("greet", END)
graph = builder.compile()
print(graph.invoke({}, context=Context(user_id="ana")))
# endregion
