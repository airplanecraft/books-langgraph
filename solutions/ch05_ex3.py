"""Exercise 5.3: a chat graph with one thread per customer and a stand-in model.
Book: Chapter 5, section 5.2
Run: python solutions/ch05_ex3.py
"""
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from common import ScriptedModel, say  # the helpers of chapter 0

model = ScriptedModel(script=[say("Hi Ana."), say("Your name is Ana."),
                              say("Hi Ben.")])


def chat(state: MessagesState) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("chat", chat)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)
graph = builder.compile(checkpointer=InMemorySaver())

turns = [("ana", "Hi, I am Ana."), ("ana", "Who am I?"), ("ben", "Hi, I am Ben.")]
for thread_id, text in turns:
    config = {"configurable": {"thread_id": thread_id}}
    graph.invoke({"messages": [{"role": "user", "content": text}]}, config)
for thread_id in ["ana", "ben"]:
    config = {"configurable": {"thread_id": thread_id}}
    saved = graph.get_state(config).values["messages"]
    print(thread_id, len(saved), [message.type for message in saved])
