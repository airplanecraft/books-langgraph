"""A bare except around interrupt swallows the pause.
Book: Chapter 7, section 7.9
Run: python ch07/pitfall_except.py
"""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class State(TypedDict):
    status: str


# region: swallowed
def review(state: State) -> dict:
    try:
        answer = interrupt("Send this reply?")  # ①
    except Exception as error:  # ②
        print("caught:", type(error).__name__)
        answer = "no answer"
    return {"status": answer}


builder = StateGraph(State)
builder.add_node("review", review)
builder.add_edge(START, "review")
builder.add_edge("review", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "ana"}}
result = graph.invoke({"status": "new"}, config)
print("result:", result)  # ③
print("next:", graph.get_state(config).next)
# endregion
