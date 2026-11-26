"""Exercise 4.2: a second tool for the tool node.
Book: Chapter 4, section 4.2
Run: python solutions/ch04_ex2.py
"""
from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel, ask_for, say

ORDERS = {"A17": "shipped on 18 November", "B42": "delayed: waiting for stock"}
TOTALS = {"A17": "$20.00", "B42": "$35.50"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")


@tool
def order_total(order_id: str) -> str:
    """Look up the total price of an order by its ID, such as A17."""
    return TOTALS.get(order_id, "no order with that ID")


tools = [lookup_order, order_total]
script = [ask_for("order_total", {"order_id": "B42"}, "call_1"),
          say("The total is $35.50.")]
model = ScriptedModel(script=script).bind_tools(tools)


def call_model(state: MessagesState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition)
builder.add_edge("tools", "model")
graph = builder.compile()

question = {"role": "user", "content": "What is the total of order B42?"}
result = graph.invoke({"messages": [question]})
print(result["messages"][2].content)
print(result["messages"][-1].content)
