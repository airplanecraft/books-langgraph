"""Exercise 2.2: a node corrects an earlier message by reusing its id.
Book: Chapter 2, section 2.4
Run: python solutions/ch02_ex2.py
"""
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph


def correct(state: MessagesState) -> dict:
    return {"messages": [AIMessage("It was delayed.", id="m2")]}


builder = StateGraph(MessagesState)
builder.add_node("correct", correct)
builder.add_edge(START, "correct")
builder.add_edge("correct", END)

start = [HumanMessage("Where is order B42?", id="m1"),
         AIMessage("It shipped.", id="m2")]
result = builder.compile().invoke({"messages": start})
print(len(result["messages"]), result["messages"][-1].content)
