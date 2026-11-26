"""A thread id on a graph that has no checkpointer: ignored, and get_state refuses.
Book: Chapter 5, section 5.7
Run: python ch05/no_saver.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    notes: Annotated[list, operator.add]


# region: no_saver
def read(state: State) -> dict:
    return {"notes": ["read the email"]}


builder = StateGraph(State)
builder.add_node("read", read)
builder.add_edge(START, "read")
builder.add_edge("read", END)
plain = builder.compile()  # ①
ticket = {"customer": "Ana", "notes": []}
config = {"configurable": {"thread_id": "ana"}}
plain.invoke(ticket, config)  # ②
second = plain.invoke({"notes": ["email 2"]}, config)
print("notes:", second["notes"])
try:
    plain.get_state(config)  # ③
except ValueError as error:
    print("get_state:", error)
# endregion
