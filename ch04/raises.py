"""An exception inside a tool stops the run.
Book: Chapter 4, section 4.8
Run: python ch04/raises.py
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

# region: raises
from langchain_core.tools import tool

from common import ask_for, say  # the helpers from chapter 0


@tool
def refund_order(order_id: str) -> str:
    """Refund an order by its ID."""
    raise ConnectionError("payment service is down")  # ①


refund = ask_for("refund_order", {"order_id": "B42"}, "call_1")
graph, _ = build([refund, say("Your refund is on its way.")], [refund_order])
question = {"role": "user", "content": "Please refund order B42."}
try:
    graph.invoke({"messages": [question]})
except ConnectionError as error:  # ②
    print("run stopped:", type(error).__name__, "|", error)
# endregion
