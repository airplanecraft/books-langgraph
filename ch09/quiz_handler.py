"""Self-check run: an error handler on a node that has no retry policy.
Book: Chapter 9, section 9.5
Run: python ch09/quiz_handler.py
"""
# region: quiz
import operator
from typing import Annotated, TypedDict

from langgraph.errors import NodeError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    log: Annotated[list, operator.add]


def charge(state: State) -> dict:
    raise ValueError("card declined")


def recover(state: State, error: NodeError) -> Command:
    note = f"{error.node}: {error.error}"
    return Command(update={"log": [note]}, goto="ask_customer")


def ask_customer(state: State) -> dict:
    return {"log": ["asked for another card"]}


builder = StateGraph(State)
builder.add_node("charge", charge, error_handler=recover)
builder.add_node("ask_customer", ask_customer)
builder.add_edge(START, "charge")
builder.add_edge("ask_customer", END)
result = builder.compile().invoke({"log": ["order received"]})
print(result["log"])
# endregion
