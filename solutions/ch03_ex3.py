"""Exercise 3.3: a node that loops on itself with a Command, under a limit.
Book: Chapter 3, section 3.5
Run: python solutions/ch03_ex3.py
"""
from typing import Literal, TypedDict

from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    count: int


def count_up(state: State) -> Command[Literal["count_up", "__end__"]]:
    count = state["count"] + 1
    return Command(update={"count": count},
                   goto=END if count >= 5 else "count_up")


builder = StateGraph(State)
builder.add_node("count_up", count_up)
builder.add_edge(START, "count_up")
graph = builder.compile()

try:
    graph.invoke({"count": 0}, config={"recursion_limit": 4})
except GraphRecursionError:
    print("GraphRecursionError")
print(graph.invoke({"count": 0}))
