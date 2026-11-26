"""Show what a node may return: a dictionary, an empty one, None, or a list.
Book: Chapter 2, section 2.2
Run: python ch02/return_kinds.py
"""
# region: kinds
from typing import TypedDict

from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    category: str


def run(update: object) -> None:
    builder = StateGraph(State)
    builder.add_node("node", lambda state: update)  # ①
    builder.add_edge(START, "node")
    builder.add_edge("node", END)
    start = {"customer": "Ana", "category": "unknown"}
    try:
        print(update, "->", builder.compile().invoke(start))
    except InvalidUpdateError as error:
        print(update, "->", str(error).splitlines()[0])  # ②


for update in ({"category": "billing"}, {}, None, ["billing"]):
    run(update)
# endregion
