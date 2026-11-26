"""Three mistakes in building a graph, and the error each one gives.
Book: Chapter 1, section 1.7
Run: python ch01/mistakes.py
"""
# region: mistakes
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    category: str


def classify(state: State) -> dict:
    return {"category": "billing"}


typo = StateGraph(State)
typo.add_node("classify", classify)
typo.add_edge(START, "clasify")  # ①
try:
    typo.compile()
except ValueError as error:
    print("typo:", error)

no_start = StateGraph(State)
no_start.add_node("classify", classify)
no_start.add_edge("classify", END)  # ②
try:
    no_start.compile()
except ValueError as error:
    print("no start:", error)

try:
    no_start.invoke({"category": "unknown"})  # ③
except AttributeError as error:
    print("not compiled:", error)
# endregion
