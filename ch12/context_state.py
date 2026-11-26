"""A user id kept in the state is saved with the thread and outlives the call.
Book: Chapter 12, section 12.6
Run: python ch12/context_state.py
"""
# region: state
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict, total=False):
    user: str
    greeting: str


def greet(state: State) -> dict:
    return {"greeting": f"Hello, {state.get('user', 'nobody')}."}


builder = StateGraph(State)
builder.add_node("greet", greet)
builder.add_edge(START, "greet")
builder.add_edge("greet", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "monday"}}
print(graph.invoke({"user": "ana"}, config)["greeting"])
print(graph.invoke({}, config)["greeting"])  # ①
saved = [copy.values.get("user") for copy in graph.get_state_history(config)]
print(saved)  # ②
# endregion
