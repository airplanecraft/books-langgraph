"""Pitfall: two tickets on one thread id.
Book: Chapter 13, section 13.10
Run: python ch13/pitfall_thread.py"""
from typing import Literal

from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command

ORDERS = {"A17": "shipped on 18 November", "B42": "delayed"}


class State(MessagesState):  # ①
    ticket_id: str
    status: str


@tool
def lookup_order(order_id: str) -> str:
    """Look up the shipping status of an order by its ID, such as A17."""
    return ORDERS.get(order_id, "no order with that ID")  # ②

from common import ScriptedModel, ask_for, say  # the stand-in of chapter 0

script = []
for _ in range(4):  # new objects each time: see the text
    script += [ask_for("lookup_order", {"order_id": "A17"}),
               say("Hi, A17 has shipped.")]
model = ScriptedModel(script=script)  # ①
limit = {"recursion_limit": 10}  # ②


def classify(state: State) -> Command[Literal["to_person", "agent"]]:
    refund = "refund" in state["messages"][-1].content.lower()  # ③
    return Command(goto="to_person" if refund else "agent")


def agent(state: State) -> dict:
    reply = model.bind_tools([lookup_order]).invoke(state["messages"])  # ④
    return {"messages": [reply]}


def to_person(state: State) -> dict:
    return {"status": "handed to a person"}

from langgraph.types import interrupt

MAILS: dict[str, str] = {}  # the toy mail service: one mail for each ticket
SERVER = {"calls": 0, "failures": 0}  # the first `failures` calls fail ①


def approve(state: State) -> Command[Literal["send", "__end__"]]:
    if interrupt(state["messages"][-1].content) == "approve":  # ②
        return Command(goto="send")
    return Command(goto=END, update={"status": "rejected"})


def send(state: State) -> dict:
    SERVER["calls"] += 1
    if SERVER["calls"] <= SERVER["failures"]:
        raise ConnectionError("mail server unreachable")
    MAILS[state["ticket_id"]] = state["messages"][-1].content  # ③
    return {"status": "sent"}

from langgraph.checkpoint.memory import InMemorySaver


def run_ticket(ticket: dict, answer: str) -> dict:
    config = {"configurable": {"thread_id": ticket["ticket_id"]}, **limit}
    for step in (ticket, Command(resume=answer)):  # ①
        names = []
        for item in graph.stream(step, config, stream_mode="updates"):  # ②
            names += list(item)
        print("  ran:", names)
    return graph.get_state(config).values  # ③


def route(state: State) -> Literal["tools", "approve"]:
    return "tools" if state["messages"][-1].tool_calls else "approve"  # ④

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
graph = builder.compile(checkpointer=InMemorySaver())  # ⑤


# region: run
config = {"configurable": {"thread_id": "desk"}, **limit}  # ①
for ticket_id in ("T1", "T2"):
    ticket = {"ticket_id": ticket_id, "messages": [
        {"role": "user", "content": "Where is my order A17?"}]}
    graph.invoke(ticket, config)
    values = graph.get_state(config).values
    print("thread holds:", values["ticket_id"], "|",
          len(values["messages"]), "messages")
graph.invoke(Command(resume="approve"), config)  # ②
print("mails:", sorted(MAILS))
# endregion
