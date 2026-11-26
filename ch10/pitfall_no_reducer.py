"""Two parallel nodes: different keys work, the same plain key raises.
Book: Chapter 10, section 10.3
Run: python ch10/pitfall_no_reducer.py
"""
# region: conflict
from typing import TypedDict

from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph


class State(TypedDict):
    order_note: str
    plan_note: str
    reply: str


def build(order_key: str, plan_key: str) -> CompiledStateGraph:
    def order(state: State) -> dict:
        return {order_key: "from order"}  # ①

    def plan(state: State) -> dict:
        return {plan_key: "from plan"}  # ②

    builder = StateGraph(State)
    builder.add_node("order", order)
    builder.add_node("plan", plan)
    for name in ("order", "plan"):
        builder.add_edge(START, name)
        builder.add_edge(name, END)
    return builder.compile()


blank = {"order_note": "", "plan_note": "", "reply": ""}
for keys in (("order_note", "plan_note"), ("reply", "reply")):
    try:
        print(keys, build(*keys).invoke(blank))
    except InvalidUpdateError as error:
        print(keys, "InvalidUpdateError:", str(error).splitlines()[0])  # ③
# endregion
