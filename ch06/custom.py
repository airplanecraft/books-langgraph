"""A node reports its progress to the program with the stream writer.
Book: Chapter 6, section 6.4
Run: python ch06/custom.py
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

# region: run
start = {"report": ""}
print("invoke:", graph.invoke(start))  # ①
for item in graph.stream(start, stream_mode="custom"):  # ②
    print("custom:", item)
updates = list(graph.stream(start, stream_mode="updates"))  # ③
print("updates:", [list(update) for update in updates])
# endregion
