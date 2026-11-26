"""A subgraph with other keys: call it inside a node and translate both ways.
Book: Chapter 11, section 11.3
Run: python ch11/subgraph_transform.py
"""
# region: wrap
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class OrderState(TypedDict):
    order_id: str
    status: str


def find(state: OrderState) -> dict:
    return {"status": "delayed"}  # stands for a lookup


inner = StateGraph(OrderState)
inner.add_node("find", find)
inner.add_edge(START, "find")
orders_graph = inner.compile()


class Ticket(TypedDict):
    customer: str
    order_ref: str  # ①
    notes: Annotated[list[str], operator.add]


def ask_orders(state: Ticket) -> dict:
    answer = orders_graph.invoke({"order_id": state["order_ref"]})  # ②
    return {"notes": [f"{state['order_ref']}: {answer['status']}"]}  # ③


outer = StateGraph(Ticket)
outer.add_node("ask_orders", ask_orders)
outer.add_edge(START, "ask_orders")
outer.add_edge("ask_orders", END)
graph = outer.compile()

ticket = {"customer": "Ana", "order_ref": "B42", "notes": ["start"]}
print(graph.invoke(ticket))  # ④
# endregion
