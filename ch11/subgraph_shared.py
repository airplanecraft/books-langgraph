"""A compiled graph used as a node of another graph, with a shared key.
Book: Chapter 11, section 11.1
Run: python ch11/subgraph_shared.py
"""
# region: lookup
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


class OrderState(TypedDict):
    order_id: str
    status: str
    source: str  # ①


def find(state: OrderState) -> dict:
    print("find sees", sorted(state))  # ②
    status = ORDERS.get(state["order_id"], "no order with that ID")
    return {"status": status, "source": "order system"}


inner = StateGraph(OrderState)
inner.add_node("find", find)
inner.add_edge(START, "find")
inner.add_edge("find", END)
orders_graph = inner.compile()

print(orders_graph.invoke({"order_id": "A17"}))  # ③
# endregion


# region: parent
class Ticket(TypedDict):
    customer: str
    order_id: str
    status: str
    reply: str


def draft(state: Ticket) -> dict:
    return {"reply": f"Hi {state['customer']}, order {state['order_id']} "
                     f"is {state['status']}."}


outer = StateGraph(Ticket)
outer.add_node("orders", orders_graph)  # ①
outer.add_node("draft", draft)
outer.add_edge(START, "orders")
outer.add_edge("orders", "draft")
outer.add_edge("draft", END)
graph = outer.compile()

ticket = {"customer": "Ana", "order_id": "A17"}
result = graph.invoke(ticket)  # ②
print(result)
print(sorted(result))  # ③
# endregion
