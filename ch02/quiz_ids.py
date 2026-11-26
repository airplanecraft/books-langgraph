"""Self-check run: add_messages with one known id and one new id.
Book: Chapter 2, section 2.4
Run: python ch02/quiz_ids.py
"""
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.message import add_messages

# region: ids
left = [HumanMessage("x", id="m1"), AIMessage("y", id="m2")]
right = [AIMessage("z", id="m1"), AIMessage("w", id="m3")]
print([(m.id, m.content) for m in add_messages(left, right)])
# endregion
