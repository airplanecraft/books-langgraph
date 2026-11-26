"""The support agent and the billing agent with the real model.
Book: Chapter 11, section 11.8
Run: python ch11/handoff_real.py   (or OFFLINE=1 python ch11/handoff_real.py)
"""
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, ToolRuntime, tools_condition
from langgraph.types import Command

from common import get_model


def build_agent(name: str, model: object, tools: list,
                role: str = "") -> object:
    def call_model(state: MessagesState) -> dict:
        history = state["messages"]
        print(f"  {name} reads", [message.type for message in history])  # ①
        if role:
            history = [SystemMessage(role)] + history  # ②
        return {"messages": [model.invoke(history)]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", tools_condition)
    builder.add_edge("tools", "model")
    return builder.compile()


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return {"A17": "shipped on 18 November"}.get(order_id, "unknown")


@tool
def refund_order(order_id: str) -> str:
    """Start the refund of an order by its ID."""
    return f"refund started for {order_id}"


@tool
def transfer_to_billing(runtime: ToolRuntime) -> Command:  # ①
    """Pass the customer to the billing agent, for refunds and invoices."""
    request = runtime.state["messages"][-1]  # ②
    answer = ToolMessage("Passed to billing.",
                         tool_call_id=runtime.tool_call_id)
    return Command(graph=Command.PARENT, goto="billing",  # ③
                   update={"messages": [request, answer]})  # ④


# region: real
support_tools = [transfer_to_billing]
billing_tools = [refund_order]
support = build_agent(
    "support", get_model().bind_tools(support_tools), support_tools,
    "You are the support agent. Refunds belong to the billing agent.")  # ①
billing = build_agent(
    "billing", get_model().bind_tools(billing_tools), billing_tools,
    "You are the billing agent. Start refunds with refund_order.")

outer = StateGraph(MessagesState)
outer.add_node("support", support, destinations=("billing",))
outer.add_node("billing", billing)
outer.add_edge(START, "support")
outer.add_edge("billing", END)
graph = outer.compile()

text = "I was charged twice for order A17. Please refund it."
question = {"role": "user", "content": text}
limit = {"recursion_limit": 10}  # ②
result = graph.invoke({"messages": [question]}, limit)
for message in result["messages"]:  # ③
    calls = [call["name"] for call in getattr(message, "tool_calls", [])]
    print(message.type, calls)
# endregion
