"""The agent loop of chapter 4 with a refund tool that nobody asks about.
Book: Chapter 7, section 7.1
Run: python ch07/no_question.py
"""
# region: agent
from typing import Any

from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel, ask_for, say  # helpers of chapter 0


@tool
def refund_order(order_id: str) -> str:
    """Refund the order with this ID, such as A17."""
    print("REFUND SENT for", order_id)  # ①
    return f"refund sent for {order_id}"


def build(script: list, tools: list, checkpointer: Any = None) -> Any:  # ②
    model = ScriptedModel(script=script).bind_tools(tools)

    def call_model(state: MessagesState) -> dict:
        return {"messages": [model.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", tools_condition)
    builder.add_edge("tools", "model")
    return builder.compile(checkpointer=checkpointer)


script = [ask_for("refund_order", {"order_id": "A17"}),
          say("I have refunded order A17.")]
graph = build(script, [refund_order])
question = {"role": "user", "content": "Please refund order A17."}
result = graph.invoke({"messages": [question]})  # ③
print(result["messages"][-1].content)
# endregion
