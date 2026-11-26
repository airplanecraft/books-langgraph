"""One parallel branch fails; the other branch's result is saved and not run again.
Book: Chapter 10, section 10.7
Run: python ch10/failed_branch.py
"""
# region: nodes
import operator
from collections import Counter
from typing import Annotated, Callable, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    notes: Annotated[list[str], operator.add]


runs: list[str] = []
plan_service_up = False


def make_note(label: str) -> Callable[[State], dict]:
    def note(state: State) -> dict:
        runs.append(label)  # ①
        if label == "plan" and not plan_service_up:
            raise RuntimeError("plan service down")  # ②
        return {"notes": [label]}

    return note


builder = StateGraph(State)
for label in ("read", "order", "plan", "draft"):
    builder.add_node(label, make_note(label))
builder.add_edge(START, "read")
for label in ("order", "plan"):
    builder.add_edge("read", label)
    builder.add_edge(label, "draft")
builder.add_edge("draft", END)
graph = builder.compile(checkpointer=InMemorySaver())  # ③
# endregion

# region: failed
config = {"configurable": {"thread_id": "ana"}}
try:
    graph.invoke({"notes": []}, config)
except RuntimeError as error:
    print("raised:", error)
snapshot = graph.get_state(config)
print("next:", snapshot.next)  # ①
for task in sorted(snapshot.tasks, key=lambda task: task.name):
    print(task.name, "| result:", task.result, "| error:", task.error)  # ②

plan_service_up = True
print("resumed:", graph.invoke(None, config)["notes"])  # ③
print("runs:", dict(sorted(Counter(runs).items())))
# endregion
