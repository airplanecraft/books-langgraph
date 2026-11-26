"""Self-check run: a counter in the store, a note in the state.
Book: Chapter 12, section 12.7
Run: python ch12/quiz_counter.py
"""
# region: quiz
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore


class State(TypedDict):
    seen: Annotated[list, operator.add]


def count(state: State, runtime: Runtime) -> dict:
    item = runtime.store.get(("shop",), "counter")
    number = item.value["n"] + 1 if item else 1
    runtime.store.put(("shop",), "counter", {"n": number})
    return {"seen": [number]}


builder = StateGraph(State)
builder.add_node("count", count)
builder.add_edge(START, "count")
builder.add_edge("count", END)
graph = builder.compile(checkpointer=InMemorySaver(), store=InMemoryStore())
for thread_id in ["a", "a", "b"]:
    config = {"configurable": {"thread_id": thread_id}}
    graph.invoke({"seen": []}, config)
print(graph.get_state(config).values["seen"])
# endregion
