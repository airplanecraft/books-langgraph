"""The checkpoints of one run, read back with get_state_history and get_state.
Book: Chapter 5, section 5.3
Run: python ch05/get_state.py
"""
# region: history
import operator
from typing import Annotated, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    notes: Annotated[list, operator.add]


def read(state: State, config: RunnableConfig) -> dict:
    step = config["metadata"]["langgraph_step"]  # ①
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

config = {"configurable": {"thread_id": "ana"}}  # ②
graph.invoke({"customer": "Ana", "notes": []}, config)
for saved in reversed(list(graph.get_state_history(config))):  # ③
    print(saved.metadata["step"], saved.metadata["source"], saved.next)
    print("   ", saved.values)
# endregion
