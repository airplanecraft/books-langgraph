"""A saved preference changes what the real model is asked, on any thread.
Book: Chapter 12, section 12.5
Run: python ch12/remember.py   (or OFFLINE=1 python ch12/remember.py)
"""
# region: remember
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore

from common import get_model  # the helper from chapter 0

model = get_model()


class State(MessagesState):
    user: str
    tone: str


def save(state: State, runtime: Runtime) -> dict:  # no model here
    if "tone" in state:
        where = ("users", state["user"])
        runtime.store.put(where, "prefs", {"tone": state["tone"]})
    return {}


def answer(state: State, runtime: Runtime) -> dict:  # the only model call
    item = runtime.store.get(("users", state["user"]), "prefs")
    messages = state["messages"]
    if item:
        rule = f"Answer in this style: {item.value['tone']}."
        messages = [{"role": "system", "content": rule}] + messages
        print("instruction from the store:", rule)  # ①
    print("model receives", len(messages), "messages")  # ②
    return {"messages": [model.invoke(messages)]}
# endregion

# region: calls
builder = StateGraph(State)
builder.add_node("save", save)
builder.add_node("answer", answer)
builder.add_edge(START, "save")
builder.add_edge("save", "answer")
builder.add_edge("answer", END)
graph = builder.compile(checkpointer=InMemorySaver(), store=InMemoryStore())

question = {"role": "user", "content": "Where is my order A17?"}
runs = [("monday", {"user": "ana", "tone": "one short, polite sentence"}),
        ("tuesday", {"user": "ana"}),
        ("wednesday", {"user": "ben"})]
for thread_id, given in runs:
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke({**given, "messages": [question]}, config)
    kind = type(result["messages"][-1]).__name__
    print(thread_id, "last message is an", kind)  # ①
# endregion
