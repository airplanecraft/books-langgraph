"""A shared key with operator.add is added twice; add_messages is not.
Book: Chapter 11, section 11.2
Run: python ch11/pitfall_duplicate.py
"""
# region: duplicate
import operator
from collections.abc import Callable
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage
from langgraph.graph import START, MessagesState, StateGraph


class Notes(TypedDict):
    notes: Annotated[list[str], operator.add]  # ①


def add_note(state: Notes) -> dict:
    return {"notes": ["checked"]}


def add_reply(state: MessagesState) -> dict:
    return {"messages": [AIMessage("checked")]}


def nest(schema: type, node: Callable) -> tuple:  # ②
    inner = StateGraph(schema)
    inner.add_node("check", node)
    inner.add_edge(START, "check")
    subgraph = inner.compile()
    outer = StateGraph(schema)
    outer.add_node("orders", subgraph)
    outer.add_edge(START, "orders")
    return subgraph, outer.compile()


subgraph, parent = nest(Notes, add_note)
print(subgraph.invoke({"notes": ["start"]}))  # ③
print(parent.invoke({"notes": ["start"]}))  # ④

subgraph, parent = nest(MessagesState, add_reply)
question = {"role": "user", "content": "start"}
result = parent.invoke({"messages": [question]})
print([message.content for message in result["messages"]])  # ⑤
# endregion
