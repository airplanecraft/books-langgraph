"""Exercise 13.3: a second tool, asked for in the same reply as the first.
Book: Chapter 13, section 13.2
Run: python solutions/ch13_ex3.py
"""
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel, say

ORDERS = {"A17": "shipped on 18 November", "B42": "delayed"}
DAYS = {"A17": "about 2 days", "B42": "about 5 days"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")


@tool
def shipping_days(order_id: str) -> str:
    """Say how many days an order still needs, by its ID, such as A17."""
    return DAYS.get(order_id, "unknown")


tools = [lookup_order, shipping_days]
calls = [
    {"name": "lookup_order", "args": {"order_id": "A17"}, "id": "call_1"},
    {"name": "shipping_days", "args": {"order_id": "A17"}, "id": "call_2"},
]
model = ScriptedModel(script=[AIMessage(content="", tool_calls=calls),
                              say("Hi Ana, A17 has shipped.")])


def agent(state: MessagesState) -> dict:
    reply = model.bind_tools(tools).invoke(state["messages"])
    return {"messages": [reply]}


builder = StateGraph(MessagesState)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
graph = builder.compile()

question = {"messages": [{"role": "user", "content": "Where is A17?"}]}
result = graph.invoke(question, {"recursion_limit": 10})
print([m.content for m in result["messages"] if m.type == "tool"])
