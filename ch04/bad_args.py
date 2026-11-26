"""A bad request becomes a tool message and the loop goes on.
Book: Chapter 4, section 4.8
Run: python ch04/bad_args.py
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

# region: bad_args
from common import ask_for, say  # the helpers from chapter 0

question = {"role": "user", "content": "Where is my order B42?"}
wrong_type = ask_for("lookup_order", {"order_id": 42}, "call_1")  # ①
wrong_name = ask_for("cancel_order", {"order_id": "B42"}, "call_1")  # ②
no_argument = ask_for("lookup_order", {}, "call_1")  # ③
for request in (wrong_type, wrong_name, no_argument):
    script = [request, say("Sorry, I could not look that up.")]
    graph, _ = build(script, [lookup_order])
    result = graph.invoke({"messages": [question]})
    tool_message = result["messages"][2]
    print(tool_message.status, "|", tool_message.content.replace("\n", " "))
    print("last message:", result["messages"][-1].content)
# endregion
