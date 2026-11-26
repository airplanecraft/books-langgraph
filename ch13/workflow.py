"""The email workflow: classify, agent loop, approve, send.
Book: Chapter 13, section 13.6
Run: python ch13/workflow.py"""
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


# region: model
from common import get_model  # the helper of chapter 0

model = get_model()  # ①
# endregion

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

from langgraph.errors import NodeError
from langgraph.types import RetryPolicy


def give_up(state: State, error: NodeError) -> Command[Literal["to_person"]]:
    return Command(goto="to_person")  # ①

retry = RetryPolicy(initial_interval=0.01, jitter=False)  # ②
builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode([lookup_order]))
builder.add_node("approve", approve)
builder.add_node("send", send, retry_policy=retry, error_handler=give_up)
builder.add_node("to_person", to_person)
builder.add_edge(START, "classify")
builder.add_conditional_edges("agent", route)
builder.add_edge("tools", "agent")
builder.add_edge("send", END)
builder.add_edge("to_person", END)  # ③
graph = builder.compile(checkpointer=InMemorySaver())


# region: demo
ticket = {"ticket_id": "T1", "messages": [
    {"role": "user", "content": "Where is my order A17?"}]}
first = run_ticket(ticket, "reject")  # ①
print("first draft:", ascii(first["messages"][-1].content))
config = {"configurable": {"thread_id": "T1"}, **limit}
history = graph.get_state_history(config)
before_agent = [s for s in history if s.next == ("agent",)][-1]  # ②
graph.invoke(None, {**before_agent.config, **limit})  # ③
SERVER.update(calls=0, failures=1)  # ④
done = graph.invoke(Command(resume="approve"), config)
request = done["messages"][1].tool_calls[0]
print(request["name"], request["args"], "->", done["messages"][2].content)
print(done["status"], "| calls:", SERVER["calls"], "| mails:", len(MAILS))
print("draft:", ascii(done["messages"][-1].content))
# endregion
