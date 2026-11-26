"""Offer one tool to the chat model and read the tool call in its reply.
Book: Chapter 0, section 0.4
Run: python ch00/first_tool.py   (or OFFLINE=1 python ch00/first_tool.py)
"""
# region: tool
from langchain_core.tools import tool

ORDERS = {"A17": "shipped on 18 November", "B42": "delayed: waiting for stock"}


@tool  # ①
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")


print("name:", lookup_order.name)  # ②
print("description:", lookup_order.description)
print("parameters:", lookup_order.args)
# endregion


# region: request
from common import get_model

model = get_model().bind_tools([lookup_order])  # ①
question = {"role": "user", "content": "Where is my order B42?"}
reply = model.invoke([question])
print("text:", repr(reply.content))  # ②
print("tool calls:", reply.tool_calls)  # ③
# endregion
