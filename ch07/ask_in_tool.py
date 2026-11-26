"""The refund tool asks a person itself, so the agent cannot skip the question.
Book: Chapter 7, section 7.7
Run: python ch07/ask_in_tool.py
"""
from typing import Any

from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel  # the stand-in model of chapter 0


# region: tool
from langchain_core.tools import tool
from langgraph.types import interrupt


@tool
def refund_order(order_id: str) -> str:
    """Refund the order with this ID, such as A17."""
    print("refund_order starts for", order_id)
    answer = interrupt(f"Refund order {order_id}?")  # ①
    if answer != "yes":
        return "a person refused the refund"  # ②
    print("REFUND SENT for", order_id)
    return f"refund sent for {order_id}"
# endregion


def build(script: list, tools: list, checkpointer: Any = None) -> Any:
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


# region: run
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from common import ask_for, say  # the helpers of chapter 0

script = [ask_for("refund_order", {"order_id": "A17"}), say("Refunded."),
          ask_for("refund_order", {"order_id": "B42"}), say("Not refunded.")]
graph = build(script, [refund_order], InMemorySaver())  # ①


def run(thread_id: str, order_id: str, answer: str) -> None:
    config = {"configurable": {"thread_id": thread_id}}
    question = {"role": "user", "content": f"Please refund order {order_id}."}
    paused = graph.invoke({"messages": [question]}, config)  # ②
    print(thread_id, "asked:", paused["__interrupt__"][0].value)
    result = graph.invoke(Command(resume=answer), config)  # ③
    print(thread_id, "tool message:", result["messages"][2].content)


run("t1", "A17", "yes")
run("t2", "B42", "no")
# endregion
