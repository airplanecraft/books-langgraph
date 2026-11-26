"""Exercise 2.3: a reducer that adds only the tags the list does not have yet.
Book: Chapter 2, section 2.3
Run: python solutions/ch02_ex3.py
"""
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


def add_new_tags(old: list[str], new: list[str]) -> list[str]:
    return old + [tag for tag in new if tag not in old]


class State(TypedDict):
    customer: str
    tags: Annotated[list[str], add_new_tags]


def read(state: State) -> dict:
    return {"tags": ["billing", "urgent"]}


def check(state: State) -> dict:
    return {"tags": ["urgent", "refund"]}


def draft(state: State) -> dict:
    return {"tags": ["billing"]}


builder = StateGraph(State)
for name, node in (("read", read), ("check", check), ("draft", draft)):
    builder.add_node(name, node)
builder.add_edge(START, "read")
builder.add_edge("read", "check")
builder.add_edge("check", "draft")
builder.add_edge("draft", END)

print(builder.compile().invoke({"customer": "Ana", "tags": []})["tags"])
