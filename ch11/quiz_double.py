"""Self-check run: a shared key with operator.add, a subgraph that adds one tag.
Book: Chapter 11, section 11.2
Run: python ch11/quiz_double.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import START, StateGraph


class Tags(TypedDict):
    tags: Annotated[list[str], operator.add]


def label(state: Tags) -> dict:
    return {"tags": ["b"]}


inner = StateGraph(Tags)
inner.add_node("label", label)
inner.add_edge(START, "label")
outer = StateGraph(Tags)
outer.add_node("lookup", inner.compile())
outer.add_edge(START, "lookup")
print(outer.compile().invoke({"tags": ["a"]})["tags"])
