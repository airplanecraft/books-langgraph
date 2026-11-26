"""Exercise 6.2: a node that reports each item it packs with the stream writer.
Book: Chapter 6, section 6.4
Run: python solutions/ch06_ex2.py
"""
from typing import TypedDict

from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    items: list[str]
    packed: int


def pack(state: State) -> dict:
    write = get_stream_writer()
    for item in state["items"]:
        write(f"packing {item}")
    return {"packed": len(state["items"])}


builder = StateGraph(State)
builder.add_node("pack", pack)
builder.add_edge(START, "pack")
builder.add_edge("pack", END)
graph = builder.compile()

start = {"items": ["A17", "B42", "C99"], "packed": 0}
for line in graph.stream(start, stream_mode="custom"):
    print(line)
print("packed", graph.invoke(start)["packed"])
