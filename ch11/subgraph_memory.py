"""What a subgraph keeps between calls: checkpointer None, True or False.
Book: Chapter 11, section 11.4
Run: python ch11/subgraph_memory.py
"""
# region: memory
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
    seen: Annotated[list[str], operator.add]  # ①


def visit(state: LookupState) -> dict:
    count = len(state["seen"]) + 1  # ②
    return {"seen": [state["question"]], "visits": count}


def run(mode: bool | None) -> None:
    inner = StateGraph(LookupState)
    inner.add_node("visit", visit).add_edge(START, "visit")
    outer = StateGraph(Ticket)
    outer.add_node("lookup", inner.compile(checkpointer=mode))  # ③
    outer.add_edge(START, "lookup")
    graph = outer.compile(checkpointer=InMemorySaver())
    visits = []
    calls = (("ana", "first"), ("ana", "second"), ("ben", "third"))
    for thread, question in calls:  # ④
        config = {"configurable": {"thread_id": thread}}
        visits.append(graph.invoke({"question": question}, config)["visits"])
    print(mode, "visits", visits)


for mode in (None, True, False):
    run(mode)
# endregion
