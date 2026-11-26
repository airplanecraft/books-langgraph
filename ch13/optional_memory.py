"""Optional: remember a customer's preferred style across tickets.
Book: Chapter 13, section 13.8
Run: python ch13/optional_memory.py
"""
# region: memory
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore


class State(TypedDict):
    customer: str
    tone: str
    rule: str


def remember(state: State, runtime: Runtime) -> dict:
    if "tone" in state:
        where = ("customers", state["customer"])  # ①
        runtime.store.put(where, "prefs", {"tone": state["tone"]})
    return {}


def draft(state: State, runtime: Runtime) -> dict:
    item = runtime.store.get(("customers", state["customer"]), "prefs")  # ②
    return {"rule": item.value["tone"] if item else "none"}  # ③


builder = StateGraph(State)
builder.add_node("remember", remember)
builder.add_node("draft", draft)
builder.add_edge(START, "remember")
builder.add_edge("remember", "draft")
builder.add_edge("draft", END)
graph = builder.compile(store=InMemoryStore())

tickets = [("monday", {"customer": "ana", "tone": "short"}),
           ("tuesday", {"customer": "ana"}),
           ("wednesday", {"customer": "ben"})]
for day, ticket in tickets:
    print(day, "-> style rule:", graph.invoke(ticket)["rule"])  # ④
# endregion
