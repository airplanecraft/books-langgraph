"""Self-check run for chapter 7: the resume value is the return value of interrupt.
Book: Chapter 7, section 7.3
Run: python ch07/quiz_value.py
"""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    price: int
    total: int


def order(state: State) -> dict:
    quantity = interrupt("How many?")
    return {"total": quantity * state["price"]}


builder = StateGraph(State)
builder.add_node("order", order)
builder.add_edge(START, "order")
builder.add_edge("order", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "q"}}
graph.invoke({"price": 4, "total": 0}, config)
print(graph.invoke(Command(resume=3), config))
