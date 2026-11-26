"""One graph, two threads: the same thread remembers, another thread does not.
Book: Chapter 5, section 5.2
Run: python ch05/threads.py   (or OFFLINE=1 python ch05/threads.py)
"""
# region: threads
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from common import get_model  # the helper from chapter 0

model = get_model()


def chat(state: MessagesState) -> dict:
    print("messages sent to the model:", len(state["messages"]))  # ①
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("chat", chat)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)
graph = builder.compile(checkpointer=InMemorySaver())  # ②


def ask(thread_id: str, text: str) -> None:
    config = {"configurable": {"thread_id": thread_id}}  # ③
    message = {"role": "user", "content": text}
    result = graph.invoke({"messages": [message]}, config)  # ④
    size = len(result["messages"])
    print(thread_id, "final state holds", size, "messages")  # ⑤
# endregion

# region: calls
ask("ana", "Hi, my name is Ana.")
ask("ana", "What is my name?")
ask("ben", "What is my name?")
# endregion
