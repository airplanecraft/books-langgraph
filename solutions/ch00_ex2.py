"""Exercise 0.2: a second tool; your program picks the tool by the name in the tool call.
Book: Chapter 0, section 0.6
Run: python solutions/ch00_ex2.py   (no key needed)
"""
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from common import ScriptedModel, ask_for, say


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return {"A17": "shipped on 18 November"}.get(order_id, "no order with that ID")


@tool
def estimate_delivery(order_id: str) -> str:
    """Give the expected delivery date of an order by its ID, such as A17."""
    return {"A17": "expected 22 November"}.get(order_id, "no order with that ID")


tools = {"lookup_order": lookup_order, "estimate_delivery": estimate_delivery}
model = ScriptedModel(script=[
    ask_for("estimate_delivery", {"order_id": "A17"}),
    say("Order A17 should arrive on 22 November."),
]).bind_tools(list(tools.values()))
messages = [{"role": "user", "content": "When will order A17 arrive?"}]
first_reply = model.invoke(messages)
call = first_reply.tool_calls[0]
result = tools[call["name"]].invoke(call["args"])
print("tool:", call["name"], "->", result)
tool_message = ToolMessage(result, tool_call_id=call["id"])
print("answer:", model.invoke(messages + [first_reply, tool_message]).content)
