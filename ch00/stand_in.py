"""The same round with the stand-in model: scripted replies, no network, no cost.
Book: Chapter 0, section 0.6
Run: python ch00/stand_in.py   (no key needed, with or without OFFLINE=1)
"""
# region: stand_in
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from common import ScriptedModel, ask_for, say

ORDERS = {"A17": "shipped on 18 November", "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")


model = ScriptedModel(script=[  # ①
    ask_for("lookup_order", {"order_id": "A17"}),
    say("Order A17 shipped on 18 November."),
])
model = model.bind_tools([lookup_order])  # ②
messages = [{"role": "user", "content": "Where is my order A17?"}]
first_reply = model.invoke(messages)
call = first_reply.tool_calls[0]
print("tool calls:", first_reply.tool_calls)
result = lookup_order.invoke(call["args"])
print("tool result:", result)
tool_message = ToolMessage(content=result, tool_call_id=call["id"])
answer = model.invoke(messages + [first_reply, tool_message])
print("tools offered:", model.tools_offered)  # ③
print("answer:", answer.content)
# endregion
