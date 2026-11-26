"""Exercise 12.3: the customer from the context, the tone from the store.
Book: Chapter 12, section 12.7
Run: python solutions/ch12_ex3.py
"""
from dataclasses import dataclass

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore

from common import ScriptedModel, say

model = ScriptedModel(script=[say("Sent."), say("Sent.")])


@dataclass(frozen=True)
class Context:
    customer_id: str


def draft(state: MessagesState, runtime: Runtime[Context]) -> dict:
    customer = runtime.context.customer_id
    item = runtime.store.get(("customers", customer), "tone")
    messages = state["messages"]
    if item:
        rule = f"Answer in this style: {item.value['tone']}."
        messages = [{"role": "system", "content": rule}] + messages
        print(customer, "->", rule)
    else:
        print(customer, "-> no instruction")
    return {"messages": [model.invoke(messages)]}


builder = StateGraph(MessagesState, context_schema=Context)
builder.add_node("draft", draft)
builder.add_edge(START, "draft")
builder.add_edge("draft", END)
store = InMemoryStore()
store.put(("customers", "ana"), "tone", {"tone": "short"})
graph = builder.compile(checkpointer=InMemorySaver(), store=store)

for thread_id, customer in [("t1", "ana"), ("t2", "ben")]:
    config = {"configurable": {"thread_id": thread_id}}
    graph.invoke({"messages": [("user", "Where is order A17?")]}, config,
                 context=Context(customer_id=customer))
