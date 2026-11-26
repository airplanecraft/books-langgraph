"""Solution 1 of chapter 11: a third question, and a subgraph that remembers.
Book: Chapter 11, section 11.4
Run: python solutions/ch11_ex1.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph


class Ticket(TypedDict):
    question: str
    visits: int


class LookupState(TypedDict):
    question: str
    visits: int
    seen: Annotated[list[str], operator.add]


def visit(state: LookupState) -> dict:
    earlier = state.get("seen", [])
    return {"seen": [state["question"]], "visits": len(earlier) + 1}


inner = StateGraph(LookupState)
inner.add_node("visit", visit)
inner.add_edge(START, "visit")
outer = StateGraph(Ticket)
outer.add_node("lookup", inner.compile(checkpointer=True))
outer.add_edge(START, "lookup")
graph = outer.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "ana"}}
visits = []
for question in ("first", "second", "third"):
    visits.append(graph.invoke({"question": question}, config)["visits"])
print(visits)
