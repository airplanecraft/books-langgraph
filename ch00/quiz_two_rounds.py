"""Backs a self-check question: two lookups in a row, messages counted before each call.
Book: Chapter 0, section 0.6
Run: python ch00/quiz_two_rounds.py   (no key needed)
"""
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from common import ScriptedModel, ask_for, say

ORDERS = {"A17": "shipped on 18 November", "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")


# region: quiz
model = ScriptedModel(script=[
    ask_for("lookup_order", {"order_id": "A17"}),
    ask_for("lookup_order", {"order_id": "C99"}, call_id="call_2"),
    say("A17 shipped on 18 November. I found no order C99."),
]).bind_tools([lookup_order])
messages = [{"role": "user", "content": "Where are A17 and C99?"}]
while True:
    print("messages sent:", len(messages))
    reply = model.invoke(messages)
    if not reply.tool_calls:
        break
    call = reply.tool_calls[0]
    result = lookup_order.invoke(call["args"])
    print("tool result:", repr(result))
    messages = messages + [reply, ToolMessage(result, tool_call_id=call["id"])]
# endregion
