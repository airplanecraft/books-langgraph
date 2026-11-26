"""Workflow step 1: classify, then an agent loop that looks up the order.
Book: Chapter 13, section 13.2
Run: python ch13/step1_loop.py"""
# region: state
from typing import Literal

from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command

ORDERS = {"A17": "shipped on 18 November", "B42": "delayed"}


class State(MessagesState):  # ①
    ticket_id: str
    status: str


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")  # ②
# endregion


# region: nodes
from common import ScriptedModel, ask_for, say  # the stand-in of chapter 0

script = []
for _ in range(4):  # new objects each time: see the text
    script += [ask_for("lookup_order", {"order_id": "A17"}),
               say("Hi, A17 has shipped.")]
model = ScriptedModel(script=script)  # ①
limit = {"recursion_limit": 10}  # ②


def classify(state: State) -> Command[Literal["to_person", "agent"]]:
    refund = "refund" in state["messages"][-1].content.lower()  # ③
    return Command(goto="to_person" if refund else "agent")


def agent(state: State) -> dict:
    reply = model.bind_tools([lookup_order]).invoke(state["messages"])  # ④
    return {"messages": [reply]}


def to_person(state: State) -> dict:
    return {"status": "handed to a person"}
# endregion


# region: build
def route(state: State) -> Literal["tools", "__end__"]:
    return "tools" if state["messages"][-1].tool_calls else END  # ①

builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode([lookup_order]))
builder.add_node("to_person", to_person)
builder.add_edge(START, "classify")
builder.add_conditional_edges("agent", route)  # ②
builder.add_edge("tools", "agent")
builder.add_edge("to_person", END)
graph = builder.compile()

emails = ["Where is my order A17?", "I want a refund for order B42."]
for text in emails:
    ticket = {"messages": [{"role": "user", "content": text}]}
    result = graph.invoke(ticket, limit)  # ③
    kinds = [type(m).__name__ for m in result["messages"]]
    print(kinds, "|", result.get("status", "-"))
    print("  last:", result["messages"][-1].content)
# endregion
