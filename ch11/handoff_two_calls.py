"""A handoff in a reply that holds a second tool call: the next agent reads an open request.
Book: Chapter 11, section 11.9
Run: python ch11/handoff_two_calls.py
"""
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, ToolRuntime, tools_condition
from langgraph.types import Command


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


# region: two_calls
from langchain_core.messages import AIMessage
from langgraph.graph import END

from common import ScriptedModel


def billing(state: MessagesState) -> None:
    messages = state["messages"]
    answered = [m.tool_call_id for m in messages if m.type == "tool"]
    asked = [call["id"] for m in messages if m.type == "ai"
             for call in m.tool_calls]
    print("  billing reads", [message.type for message in messages])  # ①
    print("  open requests:", [i for i in asked if i not in answered])  # ②


both = AIMessage(content="", tool_calls=[  # ③
    {"name": "lookup_order", "args": {"order_id": "A17"}, "id": "call_1"},
    {"name": "transfer_to_billing", "args": {}, "id": "call_2"}])
tools = [lookup_order, transfer_to_billing]
model = ScriptedModel(script=[both]).bind_tools(tools)
outer = StateGraph(MessagesState)
outer.add_node("support", build_agent("support", model, tools),
               destinations=("billing",))
outer.add_node("billing", billing)
outer.add_edge(START, "support")
outer.add_edge("billing", END)
outer.compile().invoke({"messages": [("user", "Refund A17, please.")]})
# endregion
