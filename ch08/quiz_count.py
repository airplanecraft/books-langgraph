"""Self-check run: how many copies a run from an older copy adds.
Book: Chapter 8, section 8.3
Run: python ch08/quiz_count.py
"""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

ran: list[str] = []


class State(TypedDict):
    total: int


def fetch(state: State) -> dict:
    ran.append("fetch")
    return {"total": 10}


def clean(state: State) -> dict:
    ran.append("clean")
    return {"total": state["total"] - 2}


def store(state: State) -> dict:
    ran.append("store")
    return {}


builder = StateGraph(State)
builder.add_node("fetch", fetch)
builder.add_node("clean", clean)
builder.add_node("store", store)
builder.add_edge(START, "fetch")
builder.add_edge("fetch", "clean")
builder.add_edge("clean", "store")
builder.add_edge("store", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "q3"}}
graph.invoke({"total": 0}, config)
before_store = next(snapshot for snapshot in graph.get_state_history(config)
                    if snapshot.next == ("store",))
graph.invoke(None, before_store.config)
print(len(list(graph.get_state_history(config))))
