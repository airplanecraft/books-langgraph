"""Self-check run: two threads that each add notes, and what the second one holds.
Book: Chapter 5, section 5.2
Run: python ch05/quiz_threads.py
"""
# region: quiz
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    notes: Annotated[list, operator.add]


def add_x(state: State) -> dict:
    return {"notes": ["x"]}


builder = StateGraph(State)
builder.add_node("add_x", add_x)
builder.add_edge(START, "add_x")
builder.add_edge("add_x", END)
graph = builder.compile(checkpointer=InMemorySaver())
for thread_id, note in [("ana", "a"), ("ben", "b"), ("ana", "c")]:
    config = {"configurable": {"thread_id": thread_id}}
    graph.invoke({"notes": [note]}, config)
config = {"configurable": {"thread_id": "ben"}}
print(graph.get_state(config).values["notes"])
# endregion
