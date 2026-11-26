"""Self-check run: a subgraph compiled with checkpointer=True, two threads.
Book: Chapter 11, section 11.4
Run: python ch11/quiz_memory.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph


class Ticket(TypedDict):
    visits: int


class LookupState(TypedDict):
    visits: int
    seen: Annotated[list[str], operator.add]


def visit(state: LookupState) -> dict:
    earlier = state.get("seen", [])
    return {"seen": ["visit"], "visits": len(earlier) + 1}


inner = StateGraph(LookupState)
inner.add_node("visit", visit)
inner.add_edge(START, "visit")
outer = StateGraph(Ticket)
outer.add_node("lookup", inner.compile(checkpointer=True))
outer.add_edge(START, "lookup")
graph = outer.compile(checkpointer=InMemorySaver())

counts = []
for thread in ("x", "x", "x", "y"):
    config = {"configurable": {"thread_id": thread}}
    counts.append(graph.invoke({"visits": 0}, config)["visits"])
print(counts)
