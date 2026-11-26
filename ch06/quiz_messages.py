"""Self-check run: the items of messages mode with a stand-in model and two tool calls.
Book: Chapter 6, section 6.3
Run: python ch06/quiz_messages.py
"""
from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel, say  # the stand-in model of chapter 0

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")


# region: quiz
from langchain_core.messages import AIMessage

two_calls = AIMessage(content="", tool_calls=[
    {"name": "lookup_order", "args": {"order_id": "A17"}, "id": "call_1"},
    {"name": "lookup_order", "args": {"order_id": "B42"}, "id": "call_2"}])
model = ScriptedModel(script=[two_calls, say("A17 shipped, B42 is late.")])
model = model.bind_tools([lookup_order])


def call_model(state: MessagesState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode([lookup_order]))
builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition)
builder.add_edge("tools", "model")

question = {"messages": [{"role": "user", "content": "Check my orders."}]}
items = builder.compile().stream(question, stream_mode="messages")
print(" ".join(type(message).__name__ for message, metadata in items))
# endregion
