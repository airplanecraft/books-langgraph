"""A subgraph asks a question with interrupt; the parent has the checkpointer.
Book: Chapter 11, section 11.5
Run: python ch11/subgraph_interrupt.py
"""
# region: pause
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class Ticket(TypedDict):
    order_id: str
    answer: str


def ask(state: Ticket) -> dict:
    print("  ask starts")
    reply = interrupt(f"Refund order {state['order_id']}?")  # ①
    print("  ask got", reply)
    return {"answer": reply}


inner = StateGraph(Ticket)
inner.add_node("ask", ask)
inner.add_edge(START, "ask")
orders_graph = inner.compile()  # ②

outer = StateGraph(Ticket)
outer.add_node("orders", orders_graph)  # ③
outer.add_edge(START, "orders")
outer.add_edge("orders", END)
graph = outer.compile(checkpointer=InMemorySaver())  # ④

config = {"configurable": {"thread_id": "ana"}}
result = graph.invoke({"order_id": "A17"}, config)
print("asked:", result["__interrupt__"][0].value)  # ⑤
print(graph.invoke(Command(resume="yes"), config))  # ⑥
# endregion
