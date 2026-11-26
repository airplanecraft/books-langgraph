"""Backs a self-check question: a reply with no tool call has an empty tool_calls list.
Book: Chapter 0, section 0.4
Run: python ch00/quiz_no_tool.py   (no key needed)
"""
# region: quiz
from common import ScriptedModel, ask_for, say

model = ScriptedModel(script=[
    say("Hello! How can I help?"),
    ask_for("lookup_order", {"order_id": "B42"}),
])
for number in (1, 2):
    reply = model.invoke([{"role": "user", "content": "Hi"}])
    print(number, repr(reply.content), reply.tool_calls)
# endregion
