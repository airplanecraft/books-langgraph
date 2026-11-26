"""invoke(None) needs a saved copy; on a finished thread it runs nothing.
Book: Chapter 9, section 9.7
Run: python ch09/pitfall_none.py
"""
# region: none
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str


def send(state: State) -> dict:
    print("send runs")
    return {}


builder = StateGraph(State)
builder.add_node("send", send)
builder.add_edge(START, "send")
builder.add_edge("send", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "ana"}}
try:
    graph.invoke(None, config)  # ①
except Exception as error:
    print("new thread:", type(error).__name__)
graph.invoke({"customer": "Ana"}, config)
print("second call:")
graph.invoke(None, config)  # ②
print("copies:", len(list(graph.get_state_history(config))))  # ③
# endregion
