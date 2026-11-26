"""Backs a self-check question: the id of a message and the tool_call_id of a result.
Book: Chapter 0, section 0.4
Run: python ch00/quiz_ids.py   (no key needed)
"""
# region: quiz
from langchain_core.messages import AIMessage, ToolMessage

result = ToolMessage("done", tool_call_id="call_1", id="t1")
plain = AIMessage("Hello")
print(result.id, result.tool_call_id)
print(plain.id)
# endregion
