"""Self-check run: list the edges of a chain of three nodes.
Book: Chapter 1, section 1.5
Run: python ch01/quiz_edges.py
"""
# region: edges
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    text: str


def clean(state: State) -> dict:
    return {"text": state["text"].strip()}


def shout(state: State) -> dict:
    return {"text": state["text"].upper()}


def sign(state: State) -> dict:
    return {"text": state["text"] + "!"}


builder = StateGraph(State)
builder.add_node("clean", clean)
builder.add_node("shout", shout)
builder.add_node("sign", sign)
builder.add_edge(START, "clean")
builder.add_edge("clean", "shout")
builder.add_edge("shout", "sign")
builder.add_edge("sign", END)
graph = builder.compile()
print([(edge.source, edge.target) for edge in graph.get_graph().edges])
# endregion
