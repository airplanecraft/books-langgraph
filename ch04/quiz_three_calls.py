"""Self-check run: one reply with three tool calls.
Book: Chapter 4, section 4.7
Run: python ch04/quiz_three_calls.py
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

# region: quiz
from langchain_core.messages import AIMessage

from common import ask_for, say  # the helpers from chapter 0

calls = [{"name": "lookup_order", "args": {"order_id": order_id},
          "id": f"call_{number}"}
         for number, order_id in enumerate(["A17", "B42", "A17"], start=1)]
script = [AIMessage(content="", tool_calls=calls), say("Done.")]
graph, model = build(script, [lookup_order])
question = {"role": "user", "content": "Check my orders."}
result = graph.invoke({"messages": [question]})
print(len(result["messages"]), "messages,", model.replies_used, "model calls")
# endregion
