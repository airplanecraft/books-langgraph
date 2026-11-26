"""Exercise 0.1: build the history of the second call from message objects and list their types.
Book: Chapter 0, section 0.6
Run: python solutions/ch00_ex1.py   (no key needed)
"""
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from common import ScriptedModel, ask_for, say


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return {"A17": "shipped on 18 November"}.get(order_id, "no order with that ID")


model = ScriptedModel(script=[
    ask_for("lookup_order", {"order_id": "A17"}),
    say("Order A17 shipped on 18 November."),
]).bind_tools([lookup_order])
messages = [HumanMessage("Where is my order A17?")]
first_reply = model.invoke(messages)
call = first_reply.tool_calls[0]
tool_message = ToolMessage(lookup_order.invoke(call["args"]), tool_call_id=call["id"])
messages = messages + [first_reply, tool_message]
print([message.type for message in messages])
