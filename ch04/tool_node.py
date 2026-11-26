"""A tool node on its own: it answers the tool calls of the latest AI message.
Book: Chapter 4, section 4.2
Run: python ch04/tool_node.py
"""
from langchain_core.tools import tool

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")

# region: tool_node
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

call = {"name": "lookup_order", "args": {"order_id": "A17"}, "id": "call_1"}
request = AIMessage(content="", tool_calls=[call])  # ①

builder = StateGraph(MessagesState)
builder.add_node("tools", ToolNode([lookup_order]))  # ②
builder.add_edge(START, "tools")
builder.add_edge("tools", END)
graph = builder.compile()

question = {"role": "user", "content": "Where is my order A17?"}
result = graph.invoke({"messages": [question, request]})
for message in result["messages"]:  # ③
    print(message.type, "|", message.content)
print("answers call:", result["messages"][-1].tool_call_id)
# endregion
