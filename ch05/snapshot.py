"""The state snapshot of the newest checkpoint of a thread, and delete_thread.
Book: Chapter 5, section 5.4
Run: python ch05/snapshot.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    notes: Annotated[list, operator.add]


def read(state: State) -> dict:
    return {"notes": ["read the email"]}


def draft(state: State) -> dict:
    return {"notes": ["wrote a reply"]}


builder = StateGraph(State)
builder.add_node("read", read)
builder.add_node("draft", draft)
builder.add_edge(START, "read")
builder.add_edge("read", "draft")
builder.add_edge("draft", END)
graph = builder.compile(checkpointer=InMemorySaver())

# region: snapshot
config = {"configurable": {"thread_id": "ana"}}
graph.invoke({"customer": "Ana", "notes": []}, config)
snapshot = graph.get_state(config)  # ①
print("values:", snapshot.values)
print("next:", snapshot.next)  # ②
print("metadata:", snapshot.metadata)
print("config keys:", sorted(snapshot.config["configurable"]))  # ③
unused = graph.get_state({"configurable": {"thread_id": "nobody"}})  # ④
print("unused thread:", unused.values, unused.metadata)
graph.checkpointer.delete_thread("ana")  # ⑤
print("after delete:", graph.get_state(config).values)
# endregion
