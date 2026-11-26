"""The messages mode with a stand-in model: each reply arrives as one whole message.
Book: Chapter 6, section 6.3
Run: python ch06/messages.py
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

# region: setup
from common import ScriptedModel, ask_for, say  # the helpers of chapter 0

question = {"messages": [{"role": "user", "content": "Where is B42?"}]}


def stand_in() -> ScriptedModel:
    return ScriptedModel(script=[
        ask_for("lookup_order", {"order_id": "B42"}),
        say("Order B42 is delayed: waiting for stock.")])
# endregion

# region: messages
graph = build(stand_in())
stream = graph.stream(question, stream_mode="messages")  # ①
for message, metadata in stream:
    node = metadata["langgraph_node"]  # ②
    step = metadata["langgraph_step"]  # ③
    print("messages:", type(message).__name__, "from", node, "in", step)
# endregion
