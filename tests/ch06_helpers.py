"""Helpers for the chapter 6 tests: the agent loop on a stand-in, and two small graphs.
Book: Chapter 6, section 6.6
Run: python -m pytest tests/test_ch06.py
"""
from typing import TypedDict

from langchain_core.tools import tool
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel, ask_for, say

ORDERS = {"A17": "shipped on 18 November", "B42": "delayed: waiting for stock"}
QUESTION = {"messages": [{"role": "user", "content": "Where is B42?"}]}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")


def agent(script: list | None = None):
    """The agent loop of Listing 6.1 on a stand-in model."""
    script = script or [ask_for("lookup_order", {"order_id": "B42"}), say("Done.")]
    model = ScriptedModel(script=script).bind_tools([lookup_order])

    def call_model(state: MessagesState) -> dict:
        return {"messages": [model.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode([lookup_order]))
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", tools_condition)
    builder.add_edge("tools", "model")
    return builder.compile()


class State(TypedDict):
    count: int


def counting_graph(writes: list[bool], notes: list[list[str]] | None = None):
    """One node per entry of `writes`; a node writes the state only when its entry is True.

    `notes[i]` lists what node i sends with the stream writer.
    """
    notes = notes or [[] for _ in writes]
    builder = StateGraph(State)
    names = [f"n{i}" for i in range(len(writes))]
    for i, name in enumerate(names):
        def node(state: State, i: int = i) -> dict:
            write = get_stream_writer()
            for note in notes[i]:
                write(note)
            return {"count": state["count"] + 1} if writes[i] else {}
        builder.add_node(name, node)
    for before, after in zip([START] + names, names + [END]):
        builder.add_edge(before, after)
    return builder.compile()
