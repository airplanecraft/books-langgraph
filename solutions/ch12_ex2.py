"""Exercise 12.2: a visit counter per user, with the user id in the context.
Book: Chapter 12, section 12.6
Run: python solutions/ch12_ex2.py
"""
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


def visit(state: State, runtime: Runtime[Context]) -> dict:
    user = runtime.context.user_id
    item = runtime.store.get(("visits",), user)
    count = item.value["count"] + 1 if item else 1
    runtime.store.put(("visits",), user, {"count": count})
    return {}


builder = StateGraph(State, context_schema=Context)
builder.add_node("visit", visit)
builder.add_edge(START, "visit")
builder.add_edge("visit", END)
store = InMemoryStore()
graph = builder.compile(checkpointer=InMemorySaver(), store=store)

for thread_id, user in [("t1", "ana"), ("t2", "ben"), ("t3", "ana")]:
    config = {"configurable": {"thread_id": thread_id}}
    graph.invoke({}, config, context=Context(user_id=user))
for user in ["ana", "ben"]:
    print(user, store.get(("visits",), user).value["count"])
