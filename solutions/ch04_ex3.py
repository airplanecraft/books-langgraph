"""Exercise 4.3: a tool that reports its own failure as text, so the loop goes on.
Book: Chapter 4, section 4.8
Run: python solutions/ch04_ex3.py
"""
from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel, ask_for, say


def charge_service(order_id: str) -> str:
    raise ConnectionError("payment service is down")


@tool
def refund_order(order_id: str) -> str:
    """Refund an order by its ID."""
    try:
        return charge_service(order_id)
    except ConnectionError:
        return "payment service is down, try later"


script = [ask_for("refund_order", {"order_id": "B42"}, "call_1"),
          say("The refund could not be made yet.")]
model = ScriptedModel(script=script).bind_tools([refund_order])


def call_model(state: MessagesState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode([refund_order]))
builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition)
builder.add_edge("tools", "model")
graph = builder.compile()

question = {"role": "user", "content": "Please refund order B42."}
result = graph.invoke({"messages": [question]})
print(result["messages"][2].content)
print(len(result["messages"]))
