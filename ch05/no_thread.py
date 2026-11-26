"""Two mistakes with the thread id: none at all, and one without the key thread_id.
Book: Chapter 5, section 5.7
Run: python ch05/no_thread.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    notes: Annotated[list, operator.add]


# region: no_thread
def read(state: State) -> dict:
    return {"notes": ["read the email"]}


builder = StateGraph(State)
builder.add_node("read", read)
builder.add_edge(START, "read")
builder.add_edge("read", END)
graph = builder.compile(checkpointer=InMemorySaver())
ticket = {"customer": "Ana", "notes": []}

try:
    graph.invoke(ticket)  # ①
except ValueError as error:
    print("no config:", error)
try:
    graph.invoke(ticket, {"configurable": {"user": "ana"}})  # ②
except KeyError as error:
    print("no thread_id:", repr(error))
# endregion

