"""A node that raises stops the whole run, and without a checkpointer nothing is kept.
Book: Chapter 9, section 9.1
Run: python ch09/fails.py
"""
# region: nodes
import operator
from typing import Annotated, TypedDict

mail_server = {"up": False}  # ① a switch we can turn on later


class State(TypedDict):
    customer: str
    notes: Annotated[list, operator.add]


def read(state: State) -> dict:
    print("read runs")
    return {"notes": ["read the email"]}


def send(state: State) -> dict:
    print("send runs")
    if not mail_server["up"]:
        raise ConnectionError("mail server unreachable")  # ②
    return {"notes": ["sent the reply"]}


def close(state: State) -> dict:
    print("close runs")
    return {"notes": ["closed the ticket"]}
# endregion


# region: run
from langgraph.graph import END, START, StateGraph

builder = StateGraph(State)
builder.add_node("read", read)
builder.add_node("send", send)
builder.add_node("close", close)
builder.add_edge(START, "read")
builder.add_edge("read", "send")
builder.add_edge("send", "close")
builder.add_edge("close", END)
graph = builder.compile()  # ①

try:
    graph.invoke({"customer": "Ana", "notes": []})  # ②
except ConnectionError as error:  # ③
    print("invoke raised:", error)
# endregion
