"""State, runtime context and store side by side, over three calls.
Book: Chapter 12, section 12.7
Run: python ch12/where.py
"""
# region: where
import operator
from dataclasses import dataclass
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore


@dataclass(frozen=True)
class Context:
    user_id: str


class State(TypedDict):
    notes: Annotated[list, operator.add]


def visit(state: State, runtime: Runtime[Context]) -> dict:
    where = ("users", runtime.context.user_id)
    item = runtime.store.get(where, "visits")
    count = item.value["count"] + 1 if item else 1  # ①
    runtime.store.put(where, "visits", {"count": count})
    return {"notes": [f"visit {count}"]}


builder = StateGraph(State, context_schema=Context)
builder.add_node("visit", visit)
builder.add_edge(START, "visit")
builder.add_edge("visit", END)
store = InMemoryStore()
graph = builder.compile(checkpointer=InMemorySaver(), store=store)
# endregion

# region: calls
for thread_id in ["monday", "monday", "tuesday"]:
    config = {"configurable": {"thread_id": thread_id}}
    graph.invoke({"notes": []}, config, context=Context("ana"))
    notes = graph.get_state(config).values["notes"]  # ①
    count = store.get(("users", "ana"), "visits").value["count"]  # ②
    print(thread_id, notes, "| store count:", count)

snapshot = graph.get_state(config)
print(list(snapshot.values), list(snapshot.config["configurable"]))  # ③
# endregion
