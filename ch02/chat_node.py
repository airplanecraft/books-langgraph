"""Run a graph on MessagesState whose only node calls the chat model.
Book: Chapter 2, section 2.4
Run: python ch02/chat_node.py
"""
# region: chat
from langgraph.graph import END, START, MessagesState, StateGraph

from common import get_model  # the helper from chapter 0

model = get_model()


def chat(state: MessagesState) -> dict:
    reply = model.invoke(state["messages"])  # ①
    return {"messages": [reply]}  # ②


builder = StateGraph(MessagesState)
builder.add_node("chat", chat)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)
graph = builder.compile()

text = "Greet a customer named Ana in one short sentence."
question = {"role": "user", "content": text}
result = graph.invoke({"messages": [question]})
for message in result["messages"]:
    print(message.type, "|", message.content)  # ③
# endregion
