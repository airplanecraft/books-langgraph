"""Store namespaces: a tuple per tab, prefix search, misses, limit.
Book: Chapter 12, section 12.4
Run: python ch12/namespaces.py
"""
# region: tabs
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
store.put(("users", "ana"), "prefs", {"tone": "short"})
store.put(("users", "ana"), "address", {"city": "Lyon"})
store.put(("users", "ben"), "prefs", {"tone": "formal"})


def show(label: str, items: list) -> None:
    paths = ["/".join(item.namespace + (item.key,)) for item in items]
    print(label, paths)  # ①


show("ana tab  ", store.search(("users", "ana")))  # ②
show("all users", store.search(("users",)))  # ③
show("no such  ", store.search(("users", "zed")))  # ④
show("filtered ", store.search(("users",), filter={"tone": "short"}))  # ⑤
print("typo     ", store.get(("user", "ana"), "prefs"))  # ⑥

store.put("users", "note", {"text": "no comma"})  # ⑦
print("tuple    ", store.get(("users",), "note"))
print("string   ", store.get("users", "note").namespace)

for number in range(12):  # ⑧
    store.put(("log",), f"entry{number}", {"n": number})
print("log      ", len(store.search(("log",))),
      len(store.search(("log",), limit=100)))
# endregion
