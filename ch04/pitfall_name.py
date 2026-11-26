"""A tool node with another name: tools_condition names an unknown node.
Book: Chapter 4, section 4.10
Run: python ch04/pitfall_name.py
"""
from langchain_core.tools import tool

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")

# region: name
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel, say  # the helpers from chapter 0

model = ScriptedModel(script=[say("Hello.")]).bind_tools([lookup_order])


def call_model(state: MessagesState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("runner", ToolNode([lookup_order]))  # ①
builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition)
builder.add_edge("runner", "model")
try:
    builder.compile()
except ValueError as error:  # ②
    print("ValueError:", error)
# endregion
