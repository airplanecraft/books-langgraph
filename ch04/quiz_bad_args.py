"""Self-check run: one good and one bad tool call in the same reply.
Book: Chapter 4, section 4.8
Run: python ch04/quiz_bad_args.py
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

from common import say  # the helper from chapter 0

calls = [
    {"name": "lookup_order", "args": {"order_id": "A17"}, "id": "call_1"},
    {"name": "lookup_order", "args": {"order_id": 42}, "id": "call_2"},
]
script = [AIMessage(content="", tool_calls=calls), say("One order failed.")]
graph, model = build(script, [lookup_order])
question = {"role": "user", "content": "Check my orders."}
result = graph.invoke({"messages": [question]})
statuses = [result["messages"][2].status, result["messages"][3].status]
print(*statuses, len(result["messages"]))
# endregion
