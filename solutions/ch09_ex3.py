"""Exercise 9.3: a failed run under durability="exit", with two attempts, then carried on.
Book: Chapter 9, section 9.6
Run: python solutions/ch09_ex3.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

mail_server = {"up": False}
send_runs = []


class State(TypedDict):
    customer: str
    notes: Annotated[list, operator.add]


def read(state: State) -> dict:
    return {"notes": ["read the email"]}


def send(state: State) -> dict:
    send_runs.append("run")
    if not mail_server["up"]:
        raise ConnectionError("mail server unreachable")
    return {"notes": ["sent the reply"]}


def close(state: State) -> dict:
    return {"notes": ["closed the ticket"]}


policy = RetryPolicy(max_attempts=2, initial_interval=0.01, jitter=False)
builder = StateGraph(State)
builder.add_node("read", read)
builder.add_node("send", send, retry_policy=policy)
builder.add_node("close", close)
builder.add_edge(START, "read")
builder.add_edge("read", "send")
builder.add_edge("send", "close")
builder.add_edge("close", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "ana"}}
try:
    graph.invoke({"customer": "Ana", "notes": []}, config, durability="exit")
except ConnectionError:
    pass
print("send ran", len(send_runs), "times")
print(len(list(graph.get_state_history(config))), graph.get_state(config).next)
mail_server["up"] = True
result = graph.invoke(None, config, durability="exit")
print(result["notes"])
print(graph.get_state(config).next)
