"""Call add_messages by hand: it appends, replaces by id, and converts dicts.
Book: Chapter 2, section 2.4
Run: python ch02/add_messages.py
"""
# region: merge
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.message import add_messages

old = [HumanMessage("Where is order B42?", id="m1")]
new = [AIMessage("Let me check.", id="m2")]
merged = add_messages(old, new)  # ①
print([(m.type, m.content, m.id) for m in merged])

fix = [AIMessage("It is delayed.", id="m2")]  # ②
merged = add_messages(merged, fix)
print([(m.type, m.content, m.id) for m in merged])

as_dict = [{"role": "user", "content": "Thanks"}]  # ③
merged = add_messages(merged, as_dict)
print([(m.type, m.content, m.id is not None) for m in merged][-1])
# endregion
