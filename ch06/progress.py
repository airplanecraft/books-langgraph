"""Show a run in the terminal: a note from a tool, and the reply as it is written.
Book: Chapter 6, section 6.4
Run: python ch06/progress.py   (or OFFLINE=1 python ch06/progress.py)
"""
import time
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}

# region: tool
from langgraph.config import get_stream_writer


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    get_stream_writer()(f"looking up {order_id}")  # ①
    time.sleep(1)  # the slow system behind the tool
    return ORDERS.get(order_id, "no order with that ID")
# endregion


def build(model: BaseChatModel) -> Any:
    model = model.bind_tools([lookup_order])

    def call_model(state: MessagesState) -> dict:
        return {"messages": [model.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode([lookup_order]))
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", tools_condition)
    builder.add_edge("tools", "model")
    return builder.compile()


# region: progress
from common import get_model  # the helper of chapter 0

question = {"messages": [{"role": "user", "content": "Where is B42?"}]}
modes = ["updates", "custom", "messages"]  # ①
stream = build(get_model()).stream(question, stream_mode=modes)
for mode, data in stream:  # ②
    if mode == "custom":
        print("[note]", data)
    elif mode == "updates":
        for node in data:
            print(f" [{node} finished]")
    else:
        chunk, metadata = data  # ③
        if metadata["langgraph_node"] == "model":
            print(chunk.content, end="", flush=True)  # ④
# endregion
