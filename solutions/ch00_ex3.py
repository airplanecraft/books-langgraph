"""Exercise 0.3: one function that runs a round only when the reply asks for a tool.
Book: Chapter 0, section 0.4
Run: python solutions/ch00_ex3.py   (no key needed)
"""
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from common import ScriptedModel, ask_for, say


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return {"A17": "shipped on 18 November"}.get(order_id, "no order with that ID")


def respond(model: ScriptedModel, text: str) -> str:
    messages = [{"role": "user", "content": text}]
    reply = model.invoke(messages)
    if not reply.tool_calls:
        return reply.content
    call = reply.tool_calls[0]
    tool_message = ToolMessage(lookup_order.invoke(call["args"]), tool_call_id=call["id"])
    return model.invoke(messages + [reply, tool_message]).content


asking = ScriptedModel(script=[
    ask_for("lookup_order", {"order_id": "A17"}),
    say("Order A17 shipped on 18 November."),
]).bind_tools([lookup_order])
chatty = ScriptedModel(script=[say("Hello!")]).bind_tools([lookup_order])
print("round:", respond(asking, "Where is A17?"))
print("direct:", respond(chatty, "Hi"))
