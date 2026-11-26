"""Send one message to a chat model and print its reply.
Book: Chapter 0, section 0.2
Run: python ch00/hello_model.py   (or OFFLINE=1 python ch00/hello_model.py)
"""
# region: hello
from common import get_model

model = get_model()
question = "In one sentence, what is a chat model?"
messages = [{"role": "user", "content": question}]
reply = model.invoke(messages)
print(type(reply).__name__)
print(reply.content)
print("extra fields:", sorted(reply.additional_kwargs))
print("has id:", reply.id is not None)
# endregion
