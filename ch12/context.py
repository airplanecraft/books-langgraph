"""Runtime context: the user id comes with each call.
Book: Chapter 12, section 12.6
Run: python ch12/context.py
"""
# region: context
from dataclasses import dataclass
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime


@dataclass(frozen=True)
class Context:  # ①
    user_id: str


class State(TypedDict, total=False):
    greeting: str


def greet(state: State, runtime: Runtime[Context]) -> dict:  # ②
    return {"greeting": f"Hello, {runtime.context.user_id}."}  # ③


builder = StateGraph(State, context_schema=Context)  # ④
builder.add_node("greet", greet)
builder.add_edge(START, "greet")
builder.add_edge("greet", END)
graph = builder.compile(checkpointer=InMemorySaver())

monday = {"configurable": {"thread_id": "monday"}}
tuesday = {"configurable": {"thread_id": "tuesday"}}
print(graph.invoke({}, monday, context=Context(user_id="ana")))  # ⑤
print(graph.invoke({}, tuesday, context={"user_id": "ben"}))  # ⑥
print(graph.get_state(monday).values)  # ⑦
# endregion
