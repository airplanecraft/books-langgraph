"""Two threads of one graph: what the first one learned, the second lacks.
Book: Chapter 12, section 12.1
Run: python ch12/forget.py
"""
# region: forget
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    greeting: str


def greet(state: State) -> dict:
    name = state.get("customer", "(unknown)")  # ①
    return {"greeting": f"Hello, {name}."}


builder = StateGraph(State)
builder.add_node("greet", greet)
builder.add_edge(START, "greet")
builder.add_edge("greet", END)
graph = builder.compile(checkpointer=InMemorySaver())

for thread_id, given in [("monday", {"customer": "Ana"}),
                         ("tuesday", {})]:
    config = {"configurable": {"thread_id": thread_id}}
    graph.invoke(given, config)  # ②
    saved = graph.get_state(config).values
    copies = len(list(graph.get_state_history(config)))
    print(thread_id, saved, copies, "checkpoints")  # ③
# endregion
