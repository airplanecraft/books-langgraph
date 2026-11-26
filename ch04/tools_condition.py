"""A loop builder for stand-in models, and the own route next to tools_condition.
Book: Chapter 4, section 4.4
Run: python ch04/tools_condition.py
"""
from langchain_core.tools import tool

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")

# region: helper
from collections.abc import Callable

from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel  # the stand-in model of chapter 0


def build(script: list, tools: list, router: Callable = tools_condition,
          verbose: bool = False) -> tuple:
    model = ScriptedModel(script=script).bind_tools(tools)

    def call_model(state: MessagesState) -> dict:
        if verbose:
            kinds = [message.type for message in state["messages"]]
            print("model node receives", len(kinds), kinds)
        return {"messages": [model.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", router)  # ①
    builder.add_edge("tools", "model")
    return builder.compile(), model
# endregion

# region: compare
from typing import Literal

from langgraph.graph import END

from common import ask_for, say  # the helpers from chapter 0


def route(state: MessagesState) -> Literal["tools", "__end__"]:
    return "tools" if state["messages"][-1].tool_calls else END


script = [ask_for("lookup_order", {"order_id": "A17"}, "call_1"),
          say("A17 has shipped.")]
question = {"role": "user", "content": "Where is my order A17?"}
for router in (route, tools_condition):  # ①
    graph, _ = build(script, [lookup_order], router)
    result = graph.invoke({"messages": [question]})
    kinds = [message.type for message in result["messages"]]
    print(router.__name__, kinds, result["messages"][-1].content)  # ②
# endregion
