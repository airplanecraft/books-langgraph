"""Solution 2 of chapter 11: call the subgraph in a node and return only what is new.
Book: Chapter 11, section 11.3
Run: python solutions/ch11_ex2.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import START, StateGraph


class Notes(TypedDict):
    notes: Annotated[list[str], operator.add]


def add_note(state: Notes) -> dict:
    return {"notes": ["checked"]}


inner = StateGraph(Notes)
inner.add_node("check", add_note)
inner.add_edge(START, "check")
check_graph = inner.compile()


def call_check(state: Notes) -> dict:
    answer = check_graph.invoke({"notes": state["notes"]})
    return {"notes": answer["notes"][len(state["notes"]):]}


outer = StateGraph(Notes)
outer.add_node("check", call_check)
outer.add_edge(START, "check")
print(outer.compile().invoke({"notes": ["start"]}))
