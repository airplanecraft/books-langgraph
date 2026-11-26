"""One round by hand: the model asks for a tool, your program runs it, the model answers.
Book: Chapter 0, section 0.4
Run: python ch00/one_round.py   (or OFFLINE=1 python ch00/one_round.py)
"""
# region: round
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from common import get_model

ORDERS = {"A17": "shipped on 18 November", "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")


model = get_model().bind_tools([lookup_order])
messages = [{"role": "user", "content": "Where is my order B42?"}]
first_reply = model.invoke(messages)  # ①
call = first_reply.tool_calls[0]  # ②
print("asked for:", call["name"], call["args"])
result = lookup_order.invoke(call["args"])  # ③
print("tool returned:", result)
tool_message = ToolMessage(content=result, tool_call_id=call["id"])  # ④
messages = messages + [first_reply, tool_message]  # ⑤
answer = model.invoke(messages)  # ⑥
print("messages sent in call 2:", len(messages))
print("answer:", answer.content)
# endregion
