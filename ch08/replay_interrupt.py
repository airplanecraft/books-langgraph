"""Checkpoint replay over an interrupt: the node asks again, the old answer is not reused.
Book: Chapter 8, section 8.4
Run: python ch08/replay_interrupt.py
"""
# region: pause
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    status: str


def review(state: State) -> dict:
    print("review starts")
    answer = interrupt("Send it?")  # ①
    return {"status": answer}


builder = StateGraph(State)
builder.add_node("review", review)
builder.add_edge(START, "review")
builder.add_edge("review", END)
graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "ana"}}
graph.invoke({"status": ""}, config)  # ②
print(graph.invoke(Command(resume="approved"), config)["status"])  # ③
# endregion

# region: again
history = list(graph.get_state_history(config))
before_review = next(snapshot for snapshot in history
                     if snapshot.next == ("review",))
again = graph.invoke(None, before_review.config)  # ①
print("asked again:", "__interrupt__" in again, graph.get_state(config).next)
print(graph.invoke(Command(resume="edited"), config)["status"])  # ②
# endregion
