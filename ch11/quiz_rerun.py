"""Self-check run: how often the lines of a node and of its subgraph start.
Book: Chapter 11, section 11.5
Run: python ch11/quiz_rerun.py
"""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

starts = {"wrapper": 0, "ask": 0}


class Ticket(TypedDict):
    answer: str


def ask(state: Ticket) -> dict:
    starts["ask"] += 1
    return {"answer": interrupt("Refund?")}


inner = StateGraph(Ticket)
inner.add_node("ask", ask)
inner.add_edge(START, "ask")
lookup = inner.compile()


def wrapper(state: Ticket) -> dict:
    starts["wrapper"] += 1
    return {"answer": lookup.invoke({})["answer"]}


outer = StateGraph(Ticket)
outer.add_node("wrapper", wrapper)
outer.add_edge(START, "wrapper")
outer.add_edge("wrapper", END)
graph = outer.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "ana"}}
graph.invoke({}, config)
graph.invoke(Command(resume="yes"), config)
print(f"wrapper {starts['wrapper']} ask {starts['ask']}")
