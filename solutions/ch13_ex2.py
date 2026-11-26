"""Exercise 13.2: the person may edit the draft before it is sent.
Book: Chapter 13, section 13.3
Run: python solutions/ch13_ex2.py"""
# region: state
from typing import Literal

from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command

ORDERS = {"A17": "shipped on 18 November", "B42": "delayed"}


class State(MessagesState):
    ticket_id: str
    status: str


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")
# endregion


# region: nodes
from common import ScriptedModel, ask_for, say  # the stand-in of chapter 0

script = [ask_for("lookup_order", {"order_id": "A17"}),
          say("Hi, A17 has shipped.")]
model = ScriptedModel(script=script)
limit = {"recursion_limit": 10}



def classify(state: State) -> Command[Literal["to_person", "agent"]]:
    refund = "refund" in state["messages"][-1].content.lower()
    return Command(goto="to_person" if refund else "agent")


def agent(state: State) -> dict:
    reply = model.bind_tools([lookup_order]).invoke(state["messages"])
    return {"messages": [reply]}


def to_person(state: State) -> dict:
    return {"status": "handed to a person"}
# endregion


# region: approve
from langgraph.types import interrupt

MAILS: dict[str, str] = {}
SERVER = {"calls": 0, "failures": 0}


def approve(state: State) -> Command[Literal["send", "__end__"]]:
    answer = interrupt(state["messages"][-1].content)
    action = answer.get("action") if isinstance(answer, dict) else None
    if action == "approve":
        return Command(goto="send")
    if action == "edit":
        edited = {"role": "assistant", "content": answer["text"]}
        return Command(goto="send", update={"messages": [edited]})
    return Command(goto=END, update={"status": "rejected"})


def send(state: State) -> dict:
    MAILS[state["ticket_id"]] = state["messages"][-1].content
    return {"status": "sent"}
# endregion


from langgraph.checkpoint.memory import InMemorySaver


def route(state: State) -> Literal["tools", "approve"]:
    return "tools" if state["messages"][-1].tool_calls else "approve"



builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode([lookup_order]))
builder.add_node("approve", approve)
builder.add_node("send", send)
builder.add_node("to_person", to_person)
builder.add_edge(START, "classify")
builder.add_conditional_edges("agent", route)
builder.add_edge("tools", "agent")
builder.add_edge("send", END)
builder.add_edge("to_person", END)
graph = builder.compile(checkpointer=InMemorySaver())


# region: run
ticket = {"ticket_id": "E2", "messages": [
    {"role": "user", "content": "Where is my order A17?"}]}
config = {"configurable": {"thread_id": "E2"}, **limit}
graph.invoke(ticket, config)
reply = {"action": "edit", "text": "Hi Ana, A17 ships Friday."}
done = graph.invoke(Command(resume=reply), config)
print("status:", done["status"])
print("mail:", MAILS["E2"])
# endregion
