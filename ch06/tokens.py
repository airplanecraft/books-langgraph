"""Stream the real model's reply as message chunks and gather them again.
Book: Chapter 6, section 6.3
Run: python ch06/tokens.py   (or OFFLINE=1 python ch06/tokens.py)
"""
# region: agent
import time
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    time.sleep(1)  # the slow system behind the tool
    return ORDERS.get(order_id, "no order with that ID")


def build(model: BaseChatModel) -> Any:
    model = model.bind_tools([lookup_order])

    def call_model(state: MessagesState) -> dict:
        return {"messages": [model.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode([lookup_order]))
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", tools_condition)
    builder.add_edge("tools", "model")
    return builder.compile()
# endregion

# region: tokens
from common import get_model  # the helper of chapter 0

question = {"messages": [{"role": "user", "content": "Where is B42?"}]}
stream = build(get_model()).stream(question, stream_mode="messages")  # ①
pieces = []  # the text of each chunk that has some
replies = {}  # reply id -> its chunks added together
chunks = 0
for message, metadata in stream:
    if metadata["langgraph_node"] != "model":  # ②
        continue
    chunks += 1
    if message.content:
        pieces.append(message.content)  # ③
    if message.id in replies:
        replies[message.id] += message  # ④
    else:
        replies[message.id] = message

print(chunks, "chunks,", len(pieces), "with text")
print("|".join(pieces))
first = list(replies.values())[0]
print("first reply asks for", [call["name"] for call in first.tool_calls])
# endregion
