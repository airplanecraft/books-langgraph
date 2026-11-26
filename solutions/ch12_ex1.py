"""Exercise 12.1: a store with two users, one preference overwritten.
Book: Chapter 12, section 12.2
Run: python solutions/ch12_ex1.py
"""
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
store.put(("users", "ana"), "prefs", {"tone": "short"})
store.put(("users", "ben"), "prefs", {"tone": "formal"})
store.put(("users", "ana"), "prefs", {"tone": "long"})
print(store.get(("users", "ana"), "prefs").value)
print(len(store.search(("users",))))
