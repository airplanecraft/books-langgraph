"""A store without an embedding index ignores query= in a search.
Book: Chapter 12, section 12.8
Run: python ch12/pitfall_query.py
"""
# region: query
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
store.put(("users", "ana"), "prefs", {"tone": "short"})
store.put(("users", "ana"), "address", {"city": "Lyon"})

found = store.search(("users", "ana"), query="where does she live?")  # ①
print([(item.key, item.score) for item in found])  # ②
# endregion
