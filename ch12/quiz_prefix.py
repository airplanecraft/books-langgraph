"""Self-check run: which items a search by prefix finds.
Book: Chapter 12, section 12.4
Run: python ch12/quiz_prefix.py
"""
# region: quiz
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
store.put(("shop", "north"), "hours", {"open": 9})
store.put(("shop", "south"), "hours", {"open": 10})
store.put(("shop", "north", "desk"), "hours", {"open": 8})
store.put(("shop", "north"), "hours", {"open": 7})
print(len(store.search(("shop", "north"))), "items")
# endregion
