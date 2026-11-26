"""No edge back from the tool node: the run ends after the tool message.
Book: Chapter 4, section 4.10
Run: python ch04/pitfall_edge.py
"""
from langchain_core.tools import tool

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")

# region: no_edge
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel, ask_for, say  # the helpers from chapter 0

script = [ask_for("lookup_order", {"order_id": "B42"}, "call_1"),
          say("B42 is delayed.")]
model = ScriptedModel(script=script).bind_tools([lookup_order])


def call_model(state: MessagesState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode([lookup_order]))
builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition)
graph = builder.compile()  # ①

question = {"role": "user", "content": "Where is my order B42?"}
result = graph.invoke({"messages": [question]})
print([message.type for message in result["messages"]])
print("last message:", result["messages"][-1].content)
# endregion
