"""Helpers for the chapter 4 tests: tools, a tool request, and the loop as a function.
Book: Chapter 4, section 4.8
Run: python -m pytest tests/test_ch04.py
"""
import time
from typing import Literal

from langchain_core.messages import AIMessage
from langchain_core.tools import ToolException, tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from common import ScriptedModel

RUNS: list = []  # every order id the tool is run with
ORDERS = {"A17": "shipped on 18 November", "B42": "delayed: waiting for stock"}
QUESTION = {"messages": [{"role": "user", "content": "Check my orders."}]}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    RUNS.append(order_id)
    if order_id == "A17":
        time.sleep(0.2)  # the first request is the slower one
    return ORDERS.get(order_id, "no order with that ID")


@tool
def raises_value_error(order_id: str) -> str:
    """Always fails with a ValueError."""
    raise ValueError("bad value")


@tool
def raises_tool_exception(order_id: str) -> str:
    """Always fails with a ToolException."""
    raise ToolException("tool exception")


class Row(BaseModel):
    number: int


@tool
def raises_validation_error(order_id: str) -> str:
    """Fails inside its body with a pydantic validation error."""
    Row(number="abc")  # type: ignore[arg-type]
    return "unreachable"


def request(name: str, args: dict, call_id: str = "call_1") -> AIMessage:
    call = {"name": name, "args": args, "id": call_id}
    return AIMessage(content="", tool_calls=[call])


def tool_node_graph(tools: list):
    builder = StateGraph(MessagesState)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    return builder.compile()


def agent(script: list, router=None, tool_name: str = "tools",
          edge_back: bool = True, path_map=None):
    model = ScriptedModel(script=script).bind_tools([lookup_order])

    def call_model(state: MessagesState) -> dict:
        return {"messages": [model.invoke(state["messages"])]}

    def route(state: MessagesState) -> Literal["tools", "__end__"]:
        return "tools" if state["messages"][-1].tool_calls else END

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_node(tool_name, ToolNode([lookup_order]))
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", router or route, path_map)
    if edge_back:
        builder.add_edge(tool_name, "model")
    return builder.compile(), model


def kinds(result: dict) -> list:
    return [message.type for message in result["messages"]]
