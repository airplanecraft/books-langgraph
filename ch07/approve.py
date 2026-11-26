"""A reply is drafted by the model, a person approves it, then it is sent.
Book: Chapter 7, section 7.5
Run: python ch07/approve.py   (or OFFLINE=1 python ch07/approve.py)
"""
# region: nodes
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from common import get_model  # the helper from chapter 0

model = get_model()


class State(TypedDict):
    customer: str
    email: str
    draft: str
    status: str


def draft_reply(state: State) -> dict:  # ①
    prompt = (f"Write a two-sentence reply to {state['customer']}, who "
              f"wrote: {state['email']}")
    answer = model.invoke([{"role": "user", "content": prompt}])
    return {"draft": answer.content}


def review(state: State) -> Command[Literal["send", "__end__"]]:  # ②
    question = {"question": "Send this reply?", "draft": state["draft"]}
    answer = interrupt(question)  # ③
    if answer == "approve":
        return Command(goto="send", update={"status": "approved"})
    return Command(goto=END, update={"status": "rejected"})


def send(state: State) -> dict:
    print("SENT to", state["customer"])  # stands for the mail service
    return {"status": "sent"}
# endregion

# region: run
builder = StateGraph(State)
builder.add_node("draft_reply", draft_reply)
builder.add_node("review", review)
builder.add_node("send", send)
builder.add_edge(START, "draft_reply")
builder.add_edge("draft_reply", "review")
builder.add_edge("send", END)
graph = builder.compile(checkpointer=InMemorySaver())  # ①

config = {"configurable": {"thread_id": "ana"}}
ticket = {"customer": "Ana", "email": "Where is my order B42? It is late."}
paused = graph.invoke(ticket, config)
question = paused["__interrupt__"][0].value  # ②
print("question:", question["question"])
print("draft shown:", question["draft"])
print("next:", graph.get_state(config).next)

done = graph.invoke(Command(resume="approve"), config)  # ③
print("status:", done["status"])
# endregion
