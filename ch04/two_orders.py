"""A real model asked about two orders at once.
Book: Chapter 4, section 4.7
Run: python ch04/two_orders.py   (or OFFLINE=1 python ch04/two_orders.py)
"""
from langchain_core.tools import tool

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")

from typing import Literal

from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from common import get_model  # the helper from chapter 0

model = get_model().bind_tools([lookup_order])


def call_model(state: MessagesState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


def route(state: MessagesState) -> Literal["tools", "__end__"]:  # ①
    last_message = state["messages"][-1]
    return "tools" if last_message.tool_calls else END


builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode([lookup_order]))  # ②
builder.add_edge(START, "model")
builder.add_conditional_edges("model", route)  # ③
builder.add_edge("tools", "model")  # ④
graph = builder.compile()

# region: real_two
text = "Where are my orders A17 and B42? Answer in one sentence."
question = {"role": "user", "content": text}
limit = {"recursion_limit": 10}
result = graph.invoke({"messages": [question]}, config=limit)
for message in result["messages"]:
    print(message.type, "|", message.content)
    if message.type == "ai":
        print("   tool calls:", len(message.tool_calls))  # ①
# endregion
