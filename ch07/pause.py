"""A node calls interrupt: the run pauses and invoke returns the question.
Book: Chapter 7, section 7.2
Run: python ch07/pause.py
"""
# region: pause
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class State(TypedDict):
    customer: str
    draft: str
    status: str


def review(state: State) -> dict:
    print("review starts")
    answer = interrupt("Send this reply?")  # ①
    print("review got:", answer)  # ②
    return {"status": answer}


builder = StateGraph(State)
builder.add_node("review", review)
builder.add_edge(START, "review")
builder.add_edge("review", END)
graph = builder.compile(checkpointer=InMemorySaver())  # ③

config = {"configurable": {"thread_id": "ana"}}  # ④
ticket = {"customer": "Ana", "draft": "Hi Ana, your refund is on its way."}
result = graph.invoke(ticket, config)  # ⑤
print("keys:", list(result))
pending = result["__interrupt__"]  # ⑥
print(type(pending).__name__, len(pending), type(pending[0]).__name__)
print("question:", pending[0].value)

snapshot = graph.get_state(config)  # ⑦
print("next:", snapshot.next)
print("pending:", snapshot.interrupts[0].value)
print("checkpoints:", len(list(graph.get_state_history(config))))  # ⑧
# endregion
