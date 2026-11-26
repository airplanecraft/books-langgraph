"""Copies saved under each durability mode, and whether the run can go on.
Book: Chapter 9, section 9.6
Run: python ch09/durability.py
"""
# region: graph
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

mail_server = {"up": True}


class State(TypedDict):
    customer: str


def send(state: State) -> dict:
    if not mail_server["up"]:
        raise ConnectionError("mail server unreachable")
    return {}


builder = StateGraph(State)
builder.add_node("read", lambda state: {})  # these two change nothing
builder.add_node("send", send)
builder.add_node("close", lambda state: {})
builder.add_edge(START, "read")
builder.add_edge("read", "send")
builder.add_edge("send", "close")
builder.add_edge("close", END)
# endregion


# region: modes
def run(mode: str | None, up: bool) -> None:
    mail_server["up"] = up
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "ana"}}
    try:
        graph.invoke({"customer": "Ana"}, config, durability=mode)  # ①
    except ConnectionError:
        pass
    copies = len(list(graph.get_state_history(config)))
    waiting = graph.get_state(config).next
    mail_server["up"] = True
    graph.invoke(None, config, durability=mode)  # ②
    then = graph.get_state(config).next
    print(f"{mode} up={up}: copies={copies} next={waiting} then={then}")


for mode in (None, "sync", "async", "exit"):  # ③
    run(mode, True)
    run(mode, False)
# endregion
