"""Build message objects by hand and look at their types, roles and ids.
Book: Chapter 0, section 0.2
Run: python ch00/message_ids.py   (no key needed)
"""
# region: objects
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

question = HumanMessage("Where is my order B42?")  # ①
answer = AIMessage("It is delayed.", id="m2")  # ②
result = ToolMessage("delayed: waiting for stock", tool_call_id="call_1",
                     id="t1")
for message in [question, answer, result]:
    print(type(message).__name__, message.type, repr(message.id))  # ③
# endregion
