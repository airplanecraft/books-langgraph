"""The agent loop of chapter 4 with invoke and with stream, on a slow tool.
Book: Chapter 6, section 6.1
Run: python ch06/wait.py
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

# region: compare
def tool_done(start: float) -> str:
    return "after" if time.time() - start > 0.5 else "before"


start = time.time()
result = build(stand_in()).invoke(question)  # ①
print("invoke returned", tool_done(start), "the tool finished")  # ②

start = time.time()
graph = build(stand_in())
for update in graph.stream(question, stream_mode="updates"):  # ③
    print(list(update), tool_done(start), "the tool finished")  # ④
# endregion
