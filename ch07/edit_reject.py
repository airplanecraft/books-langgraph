"""One review node, three answers: approve, edit or reject.
Book: Chapter 7, section 7.6
Run: python ch07/edit_reject.py
"""
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


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


def send(state: State) -> dict:
    print("SENT to", state["customer"])  # stands for the mail service
    return {"status": "sent"}


# region: answers
from common import ScriptedModel, say  # the stand-in model of chapter 0

model = ScriptedModel(script=[say("Hi Ana, B42 is delayed.")] * 4)


def review(state: State) -> Command[Literal["send", "__end__"]]:
    question = {"question": "Send this reply?", "draft": state["draft"]}
    answer = interrupt(question)
    action = answer.get("action") if isinstance(answer, dict) else None  # ①
    if action == "approve":
        return Command(goto="send")
    if action == "edit":
        return Command(goto="send", update={"draft": answer["text"]})  # ②
    return Command(goto=END, update={"status": "rejected"})  # ③


builder = StateGraph(State)
builder.add_node("draft_reply", draft_reply)
builder.add_node("review", review)
builder.add_node("send", send)
builder.add_edge(START, "draft_reply")
builder.add_edge("draft_reply", "review")
builder.add_edge("send", END)
graph = builder.compile(checkpointer=InMemorySaver())

ticket = {"customer": "Ana", "email": "Where is my order B42?"}


def answer_with(thread_id: str, answer: object) -> None:
    config = {"configurable": {"thread_id": thread_id}}
    graph.invoke(ticket, config)  # runs up to the question
    result = graph.invoke(Command(resume=answer), config)
    print(thread_id, "->", result["status"], "|", result["draft"])


answer_with("t1", {"action": "approve"})
answer_with("t2", {"action": "edit", "text": "Hi Ana, B42 ships Friday."})
answer_with("t3", {"action": "reject"})
answer_with("t4", "approve")  # ④
# endregion
