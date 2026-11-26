"""When the checkpointer is asked to save, under sync and under exit.
Book: Chapter 9, section 9.6
Run: python ch09/durability_order.py
"""
# region: order
from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

events: list = []


class LoggingSaver(InMemorySaver):  # notes every save in `events`
    def put(self, config: Any, checkpoint: Any, metadata: Any,
            new_versions: Any) -> Any:  # ①
        events.append(f"save {metadata['step']}")
        return super().put(config, checkpoint, metadata, new_versions)


class State(TypedDict):
    customer: str


def make_node(name: str) -> Any:
    def node(state: State) -> dict:
        events.append(f"{name} runs")  # ②
        return {}
    return node


builder = StateGraph(State)
builder.add_node("read", make_node("read"))
builder.add_node("send", make_node("send"))
builder.add_edge(START, "read")
builder.add_edge("read", "send")
builder.add_edge("send", END)

for mode in ("sync", "exit"):
    events.clear()
    graph = builder.compile(checkpointer=LoggingSaver())
    config = {"configurable": {"thread_id": "ana"}}
    graph.invoke({"customer": "Ana"}, config, durability=mode)
    print(mode + ":", ", ".join(events))  # ③
# endregion
