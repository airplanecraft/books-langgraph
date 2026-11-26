"""Without a checkpointer the run still pauses, but it cannot be resumed.
Book: Chapter 7, section 7.9
Run: python ch07/no_checkpointer.py
"""
# region: missing
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    status: str


def review(state: State) -> dict:
    answer = interrupt("Send this reply?")
    return {"status": answer}


builder = StateGraph(State)
builder.add_node("review", review)
builder.add_edge(START, "review")
builder.add_edge("review", END)
graph = builder.compile()  # ①

config = {"configurable": {"thread_id": "ana"}}
result = graph.invoke({"status": "new"}, config)
print("paused:", result["__interrupt__"][0].value)  # ②
try:
    graph.invoke(Command(resume="approve"), config)  # ③
except RuntimeError as error:
    print("RuntimeError:", error)
# endregion
