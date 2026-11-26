"""Self-check run: a second call on a thread, without the first context.
Book: Chapter 12, section 12.6
Run: python ch12/quiz_context.py
"""
# region: quiz
from dataclasses import dataclass
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime


@dataclass
class Context:
    shop: str = "none"


class State(TypedDict, total=False):
    seen: str


def look(state: State, runtime: Runtime[Context]) -> dict:
    context = runtime.context
    return {"seen": context.shop if context else "nothing"}


builder = StateGraph(State, context_schema=Context)
builder.add_node("look", look)
builder.add_edge(START, "look")
builder.add_edge("look", END)
graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "t1"}}
graph.invoke({}, config, context=Context(shop="north"))
print(graph.invoke({}, config))
# endregion
