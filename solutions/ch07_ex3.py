"""Exercise 7.3: a refund tool that asks a person only for large amounts.
Book: Chapter 7, section 7.7
Run: python solutions/ch07_ex3.py
"""
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt

from common import ScriptedModel, ask_for, say  # the helpers of chapter 0


@tool
def refund_order(order_id: str, amount: int) -> str:
    """Refund an order by ID, such as A17, for an amount in dollars."""
    if amount > 100:
        answer = interrupt(f"Refund {amount} for order {order_id}?")
        if answer != "yes":
            return "a person refused the refund"
    return f"refund sent for {order_id} ({amount})"


script = [ask_for("refund_order", {"order_id": "A17", "amount": 20}),
          say("Done."),
          ask_for("refund_order", {"order_id": "B42", "amount": 250}),
          say("Done.")]
model = ScriptedModel(script=script).bind_tools([refund_order])


def call_model(state: MessagesState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode([refund_order]))
builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition)
builder.add_edge("tools", "model")
graph = builder.compile(checkpointer=InMemorySaver())

for order_id in ["A17", "B42"]:
    config = {"configurable": {"thread_id": order_id}}
    question = {"role": "user", "content": f"Refund {order_id}."}
    result = graph.invoke({"messages": [question]}, config)
    if "__interrupt__" in result:
        print(order_id, "asked:", result["__interrupt__"][0].value)
        result = graph.invoke(Command(resume="yes"), config)
    print(order_id, "tool message:", result["messages"][2].content)
