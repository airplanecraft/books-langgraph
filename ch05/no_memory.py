"""Two invokes of the agent graph of chapter 4: the second knows nothing of the first.
Book: Chapter 5, section 5.1
Run: python ch05/no_memory.py
"""
from langchain_core.tools import tool

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")

# region: forget
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from common import ScriptedModel, ask_for, say  # the helpers of chapter 0

script = [ask_for("lookup_order", {"order_id": "A17"}),
          say("A17 has shipped."), say("B42 is delayed.")]
model = ScriptedModel(script=script).bind_tools([lookup_order])


def call_model(state: MessagesState) -> dict:
    kinds = [message.type for message in state["messages"]]
    print("model node receives", len(kinds), kinds)  # ①
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode([lookup_order]))
builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition)
builder.add_edge("tools", "model")
graph = builder.compile()

for text in ["Where is order A17?", "And order B42?"]:
    result = graph.invoke({"messages": [{"role": "user", "content": text}]})
    print("final state holds", len(result["messages"]), "messages")  # ②
# endregion
