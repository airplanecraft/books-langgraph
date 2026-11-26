"""Which lines start again on a resume when a node calls the subgraph itself.
Book: Chapter 11, section 11.5
Run: python ch11/subgraph_rerun.py
"""
# region: wrapper
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class Ticket(TypedDict):
    order_id: str
    answer: str


def ask(state: Ticket) -> dict:
    print("  ask starts")
    return {"answer": interrupt(f"Refund order {state['order_id']}?")}


inner = StateGraph(Ticket)
inner.add_node("ask", ask)
inner.add_edge(START, "ask")
orders_graph = inner.compile()


def call_orders(state: Ticket) -> dict:  # ①
    print("  call_orders starts")
    answer = orders_graph.invoke({"order_id": state["order_id"]})  # ②
    return {"answer": answer["answer"]}


outer = StateGraph(Ticket)
outer.add_node("call_orders", call_orders)
outer.add_edge(START, "call_orders")
outer.add_edge("call_orders", END)
graph = outer.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "ben"}}
result = graph.invoke({"order_id": "B42"}, config)
print("asked:", result["__interrupt__"][0].value)  # ③
print(graph.invoke(Command(resume="no"), config))  # ④
# endregion
