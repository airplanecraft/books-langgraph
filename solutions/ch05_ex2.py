"""Exercise 5.2: a visit counter that keeps counting on its own thread.
Book: Chapter 5, section 5.5
Run: python solutions/ch05_ex2.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    visits: Annotated[int, operator.add]


def count_visit(state: State) -> dict:
    return {"visits": 1}


builder = StateGraph(State)
builder.add_node("count_visit", count_visit)
builder.add_edge(START, "count_visit")
builder.add_edge("count_visit", END)
graph = builder.compile(checkpointer=InMemorySaver())

for thread_id in ["ana", "ana", "ana", "ben"]:
    config = {"configurable": {"thread_id": thread_id}}
    graph.invoke({"customer": thread_id}, config)
for thread_id in ["ana", "ben"]:
    config = {"configurable": {"thread_id": thread_id}}
    print(thread_id, graph.get_state(config).values["visits"])
