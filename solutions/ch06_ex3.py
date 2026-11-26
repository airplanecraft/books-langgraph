"""Exercise 6.3: print one line for each node run of the agent loop, from the updates.
Book: Chapter 6, section 6.5
Run: python solutions/ch06_ex3.py
"""
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel, ask_for, say

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
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


def show(graph: Any, question: dict) -> None:
    for update in graph.stream(question, stream_mode="updates"):
        for node, change in update.items():
            message = change["messages"][-1]
            if node == "tools":
                print("tool says:", message.content)
            elif message.tool_calls:
                print("asks for", message.tool_calls[0]["name"])
            else:
                print("answer:", message.content)


model = ScriptedModel(script=[
    ask_for("lookup_order", {"order_id": "B42"}),
    say("Order B42 is delayed: waiting for stock.")])
question = {"messages": [{"role": "user", "content": "Where is B42?"}]}
show(build(model), question)
