"""Two agents as subgraphs; the support agent hands the conversation to billing.
Book: Chapter 11, section 11.6
Run: python ch11/handoff.py
"""
# region: agent
from langchain_core.messages import SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition


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
# endregion


# region: tools
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command


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
# endregion


# region: team
from langgraph.graph import END

from common import ScriptedModel, ask_for, say  # the stand-in of chapter 0

support_tools = [lookup_order, transfer_to_billing]
support_script = [ask_for("lookup_order", {"order_id": "A17"}, "call_1"),
                  ask_for("transfer_to_billing", {}, "call_2")]
support = build_agent(
    "support", ScriptedModel(script=support_script).bind_tools(support_tools),
    support_tools)  # ①
billing_script = [ask_for("refund_order", {"order_id": "A17"}, "call_3"),
                  say("Your refund for A17 is on its way.")]
billing_model = ScriptedModel(script=billing_script)
billing_model = billing_model.bind_tools([refund_order])
billing = build_agent("billing", billing_model, [refund_order])

outer = StateGraph(MessagesState)
outer.add_node("support", support, destinations=("billing",))  # ②
outer.add_node("billing", billing)
outer.add_edge(START, "support")
outer.add_edge("billing", END)
graph = outer.compile()

question = {"role": "user", "content": "Please refund my order A17."}
result = graph.invoke({"messages": [question]})
for message in result["messages"]:  # ③
    shown = message.content or message.tool_calls[0]["name"]
    print(message.type, "|", shown)
# endregion
