"""Two misses: a later call without context, and a graph without a store.
Book: Chapter 12, section 12.8
Run: python ch12/pitfall_missing.py
"""
# region: missing
from dataclasses import dataclass
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore


@dataclass(frozen=True)
class Context:
    user_id: str


class State(TypedDict, total=False):
    done: bool


def work(state: State, runtime: Runtime[Context]) -> dict:
    user = runtime.context.user_id  # ①
    runtime.store.put(("users", user), "seen", {"yes": True})  # ②
    return {"done": True}


builder = StateGraph(State, context_schema=Context)
builder.add_node("work", work)
builder.add_edge(START, "work")
builder.add_edge("work", END)
full = builder.compile(checkpointer=InMemorySaver(), store=InMemoryStore())
no_store = builder.compile()  # ③
# endregion

# region: calls
config = {"configurable": {"thread_id": "monday"}}
calls = [(full, Context("ana")), (full, None), (no_store, Context("ana"))]
for graph, given in calls:
    try:
        print(graph.invoke({}, config, context=given))  # ①
    except AttributeError as error:
        print("AttributeError:", error)
# endregion
