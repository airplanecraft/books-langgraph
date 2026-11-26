"""What a failed run leaves in the checkpointer: values, next, the task error.
Book: Chapter 9, section 9.2
Run: python ch09/node_error.py
"""
# region: nodes
import operator
from typing import Annotated, TypedDict

mail_server = {"up": False}  # ① a switch we can turn on later


class State(TypedDict):
    customer: str
    notes: Annotated[list, operator.add]


def read(state: State) -> dict:
    print("read runs")
    return {"notes": ["read the email"]}


def send(state: State) -> dict:
    print("send runs")
    if not mail_server["up"]:
        raise ConnectionError("mail server unreachable")  # ②
    return {"notes": ["sent the reply"]}


def close(state: State) -> dict:
    print("close runs")
    return {"notes": ["closed the ticket"]}
# endregion


from langgraph.graph import END, START, StateGraph

builder = StateGraph(State)
builder.add_node("read", read)
builder.add_node("send", send)
builder.add_node("close", close)
builder.add_edge(START, "read")
builder.add_edge("read", "send")
builder.add_edge("send", "close")
builder.add_edge("close", END)


# region: saved
from langgraph.checkpoint.memory import InMemorySaver

graph = builder.compile(checkpointer=InMemorySaver())  # ①

config = {"configurable": {"thread_id": "ana"}}
try:
    graph.invoke({"customer": "Ana", "notes": []}, config)
except ConnectionError as error:
    print("invoke raised:", error)
snapshot = graph.get_state(config)  # ②
print("values:", snapshot.values)
print("next:", snapshot.next)
for task in snapshot.tasks:  # ③
    print("task:", task.name, "| error:", task.error)
    print("type of the error:", type(task.error).__name__)
for saved in reversed(list(graph.get_state_history(config))):  # ④
    print("copy at step", saved.metadata["step"], "next:", saved.next)
# endregion
