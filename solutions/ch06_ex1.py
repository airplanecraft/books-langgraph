"""Exercise 6.1: the agent loop of Listing 6.1, streamed in two modes; print the mode names.
Book: Chapter 6, section 6.5
Run: python solutions/ch06_ex1.py
"""
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel, ask_for, say

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")


def build(model: BaseChatModel) -> Any:
    model = model.bind_tools([lookup_order])

    def call_model(state: MessagesState) -> dict:
        return {"messages": [model.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode([lookup_order]))
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", tools_condition)
    builder.add_edge("tools", "model")
    return builder.compile()


model = ScriptedModel(script=[
    ask_for("lookup_order", {"order_id": "B42"}),
    say("Order B42 is delayed: waiting for stock.")])
question = {"messages": [{"role": "user", "content": "Where is B42?"}]}
items = build(model).stream(question, stream_mode=["updates", "values"])
print(" ".join(mode for mode, data in items))
