"""One graph, three threads: a preference saved in one is read in another.
Book: Chapter 12, section 12.3
Run: python ch12/share.py
"""
# region: share
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore


class State(TypedDict, total=False):
    user: str
    tone: str
    note: str


def save(state: State, runtime: Runtime) -> dict:  # ①
    if "tone" in state:
        where = ("users", state["user"])
        runtime.store.put(where, "prefs", {"tone": state["tone"]})  # ②
    return {}


def recall(state: State, runtime: Runtime) -> dict:
    item = runtime.store.get(("users", state["user"]), "prefs")  # ③
    tone = item.value["tone"] if item else "none saved"
    return {"note": f"{state['user']}: {tone}"}


builder = StateGraph(State)
builder.add_node("save", save)
builder.add_node("recall", recall)
builder.add_edge(START, "save")
builder.add_edge("save", "recall")
builder.add_edge("recall", END)
store = InMemoryStore()
graph = builder.compile(checkpointer=InMemorySaver(), store=store)  # ④
# endregion

# region: calls
runs = [("monday", {"user": "ana", "tone": "short"}),
        ("tuesday", {"user": "ana"}),
        ("wednesday", {"user": "ben"})]
for thread_id, given in runs:
    config = {"configurable": {"thread_id": thread_id}}
    note = graph.invoke(given, config)["note"]
    copies = len(list(graph.get_state_history(config)))
    print(thread_id, note, f"({copies} checkpoints)")
tuesday = {"configurable": {"thread_id": "tuesday"}}
print(graph.get_state(tuesday).values)  # ①
# endregion
