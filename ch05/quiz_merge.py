"""Self-check run: a second invoke on the same thread, with a counter that adds.
Book: Chapter 5, section 5.5
Run: python ch05/quiz_merge.py
"""
# region: quiz
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    total: Annotated[int, operator.add]
    label: str


def count(state: State) -> dict:
    return {"total": 1}


builder = StateGraph(State)
builder.add_node("count", count)
builder.add_edge(START, "count")
builder.add_edge("count", END)
graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "t1"}}
graph.invoke({"total": 10, "label": "a"}, config)
print(graph.invoke({"total": 5}, config))
# endregion
