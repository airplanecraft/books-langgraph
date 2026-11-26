"""Write down the keys of a ticket with a TypedDict class and fill them in.
Book: Chapter 1, section 1.1
Run: python ch01/state_dict.py
"""
# region: state
from typing import TypedDict


class State(TypedDict):  # ①
    customer: str
    body: str
    category: str
    reply: str


ticket: State = {  # ②
    "customer": "Ana",
    "body": "I was charged twice for May.",
    "category": "unknown",
    "reply": "",
}
print(type(ticket))  # ③
for key, value in ticket.items():
    print(key, "=", repr(value))
# endregion
