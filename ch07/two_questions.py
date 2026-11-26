"""Two interrupts in one node: each resume value goes to the next interrupt.
Book: Chapter 7, section 7.8
Run: python ch07/two_questions.py
"""
# region: two
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    answers: list


def collect(state: State) -> dict:
    print("collect starts")
    order = interrupt("Which order?")  # ①
    print("first answer:", order)
    reason = interrupt("Which reason?")  # ②
    print("second answer:", reason)
    return {"answers": [order, reason]}


builder = StateGraph(State)
builder.add_node("collect", collect)
builder.add_edge(START, "collect")
builder.add_edge("collect", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "ana"}}
result = graph.invoke({"answers": []}, config)
print("asked:", result["__interrupt__"][0].value)
result = graph.invoke(Command(resume="B42"), config)  # ③
print("asked:", result["__interrupt__"][0].value)
result = graph.invoke(Command(resume="late"), config)  # ④
print("final:", result["answers"])
# endregion
