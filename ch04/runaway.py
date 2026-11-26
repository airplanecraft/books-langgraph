"""A model that never stops asking for a tool: the recursion limit ends the loop.
Book: Chapter 4, section 4.5
Run: python ch04/runaway.py
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

# region: runaway
from langgraph.errors import GraphRecursionError

from common import ask_for  # the helper from chapter 0

script = [ask_for("lookup_order", {"order_id": "B42"}, f"call_{number}")
          for number in range(1, 11)]  # ten requests and no answer
graph, model = build(script, [lookup_order])
question = {"role": "user", "content": "Where is my order B42?"}
try:
    graph.invoke({"messages": [question]}, config={"recursion_limit": 6})  # ①
except GraphRecursionError as error:
    print(str(error).splitlines()[0])  # ②
print("model calls:", model.replies_used)  # ③
# endregion
