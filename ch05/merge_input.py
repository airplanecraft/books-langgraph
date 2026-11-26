"""A second invoke on the same thread: the input is merged, the graph runs again.
Book: Chapter 5, section 5.5
Run: python ch05/merge_input.py
"""
import operator
from typing import Annotated, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    notes: Annotated[list, operator.add]


def read(state: State, config: RunnableConfig) -> dict:
    step = config["metadata"]["langgraph_step"]
    print("read runs in super-step", step)
    return {"notes": ["read the email"]}


def draft(state: State, config: RunnableConfig) -> dict:
    step = config["metadata"]["langgraph_step"]
    print("draft runs in super-step", step)
    return {"notes": ["wrote a reply"]}


builder = StateGraph(State)
builder.add_node("read", read)
builder.add_node("draft", draft)
builder.add_edge(START, "read")
builder.add_edge("read", "draft")
builder.add_edge("draft", END)
graph = builder.compile(checkpointer=InMemorySaver())

# region: merge
config = {"configurable": {"thread_id": "ana"}}
graph.invoke({"customer": "Ana", "notes": ["email 1"]}, config)
print("second invoke")
second = graph.invoke({"notes": ["email 2"]}, config)  # ①
print("customer:", second["customer"])  # ②
print("notes:", second["notes"])  # ③
print("checkpoints:", len(list(graph.get_state_history(config))))  # ④
# endregion
