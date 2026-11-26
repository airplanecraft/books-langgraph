"""A memory store on its own: put, get and what a miss looks like.
Book: Chapter 12, section 12.2
Run: python ch12/store_basics.py
"""
# region: basics
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()  # ①
store.put(("users", "ana"), "prefs", {"tone": "short"})  # ②
item = store.get(("users", "ana"), "prefs")  # ③
print(item.value, item.key, item.namespace)

store.put(("users", "ana"), "prefs", {"tone": "formal"})  # ④
print(store.get(("users", "ana"), "prefs").value)

print(store.get(("users", "ben"), "prefs"))  # ⑤
print(InMemoryStore().get(("users", "ana"), "prefs"))  # ⑥
# endregion
