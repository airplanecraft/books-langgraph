"""What the update of a handoff decides: what the billing node reads.
Book: Chapter 11, section 11.7
Run: python ch11/handoff_update.py
"""
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, ToolRuntime, tools_condition
from langgraph.types import Command

from common import ScriptedModel, ask_for




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
    return "shipped on 18 November"


# region: compare
from langgraph.graph import END

from common import ScriptedModel, ask_for


def make_handoff(share: str) -> object:
    @tool
    def transfer_to_billing(runtime: ToolRuntime) -> Command:
        """Pass the customer to the billing agent."""
        history = runtime.state["messages"]
        answer = ToolMessage("Passed to billing.",
                             tool_call_id=runtime.tool_call_id)
        choices = {"pair": [history[-1], answer],  # ①
                   "nothing": [],  # ②
                   "all": history + [answer]}  # ③
        return Command(graph=Command.PARENT, goto="billing",
                       update={"messages": choices[share]})
    return transfer_to_billing


def billing(state: MessagesState) -> None:
    kinds = [message.type for message in state["messages"]]
    print("  billing reads", kinds)


script = [ask_for("lookup_order", {"order_id": "A17"}, "call_1"),
          ask_for("transfer_to_billing", {}, "call_2")]
for share in ("pair", "nothing", "all"):  # ④
    print(share)
    tools = [lookup_order, make_handoff(share)]
    model = ScriptedModel(script=script).bind_tools(tools)
    outer = StateGraph(MessagesState)
    outer.add_node("support", build_agent("support", model, tools),
                   destinations=("billing",))
    outer.add_node("billing", billing)
    outer.add_edge(START, "support")
    outer.add_edge("billing", END)
    outer.compile().invoke({"messages": [("user", "Refund A17, please.")]})
# endregion
