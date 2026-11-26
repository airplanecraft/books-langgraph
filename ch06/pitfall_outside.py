"""Mistake: the stream writer called outside a run
Book: Chapter 6, section 6.6
Run: python ch06/pitfall_outside.py
"""
# region: writer
from typing import TypedDict

from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


class State(TypedDict):
    report: str


def check_orders(state: State) -> dict:
    write = get_stream_writer()  # ①
    lines = []
    for order_id, status in ORDERS.items():
        write(f"checking {order_id}")  # ②
        lines.append(f"{order_id} {status}")
    write({"checked": len(lines)})  # ③
    return {"report": "; ".join(lines)}


builder = StateGraph(State)
builder.add_node("check_orders", check_orders)
builder.add_edge(START, "check_orders")
builder.add_edge("check_orders", END)
graph = builder.compile()
# endregion

# region: pitfall_outside
try:
    check_orders({"report": ""})  # ①
except RuntimeError as error:
    print("RuntimeError:", error)
# endregion
