"""A graph with one node that calls a model which may ask for a tool.
Book: Chapter 4, section 4.1
Run: python ch04/model_node.py   (or OFFLINE=1 python ch04/model_node.py)
"""
# region: tool
from langchain_core.tools import tool

ORDERS = {"A17": "shipped on 18 November",
          "B42": "delayed: waiting for stock"}


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")
# endregion

# region: model_node
from langgraph.graph import END, START, MessagesState, StateGraph

from common import get_model  # the helper from chapter 0

model = get_model().bind_tools([lookup_order])  # ①


def call_model(state: MessagesState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}  # ②


builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_edge(START, "model")
builder.add_edge("model", END)
graph = builder.compile()

question = {"role": "user", "content": "Where is my order B42?"}
result = graph.invoke({"messages": [question]})
for message in result["messages"]:  # ③
    print(message.type, "|", message.content)
    if message.type == "ai":
        calls = [(call["name"], call["args"]) for call in message.tool_calls]
        print("tool calls:", calls)
# endregion
