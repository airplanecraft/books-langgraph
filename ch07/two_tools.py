"""One reply asks for two tools and one of them asks a person: both start again.
Book: Chapter 7, section 7.7
Run: python ch07/two_tools.py
"""
from typing import Any

from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt

from common import ScriptedModel  # the stand-in model of chapter 0


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


@tool
def refund_order(order_id: str) -> str:
    """Refund the order with this ID, such as A17."""
    print("refund_order starts for", order_id)
    answer = interrupt(f"Refund order {order_id}?")
    if answer != "yes":
        return "a person refused the refund"
    print("REFUND SENT for", order_id)
    return f"refund sent for {order_id}"


# region: two
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from common import say  # the helper of chapter 0

started: list = []


@tool
def note_order(order_id: str) -> str:
    """Write a note on the order with this ID, such as A17."""
    started.append("note_order")  # ①
    return f"note written on {order_id}"


calls = [{"name": "note_order", "args": {"order_id": "A17"}, "id": "c1"},
         {"name": "refund_order", "args": {"order_id": "A17"}, "id": "c2"}]
script = [AIMessage(content="", tool_calls=calls), say("Done.")]  # ②
graph = build(script, [note_order, refund_order], InMemorySaver())

config = {"configurable": {"thread_id": "ana"}}
question = {"role": "user", "content": "Note and refund order A17."}
graph.invoke({"messages": [question]}, config)
graph.invoke(Command(resume="yes"), config)  # ③
print("note_order started", len(started), "times")  # ④
# endregion
