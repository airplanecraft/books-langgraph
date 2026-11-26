"""More tests for chapter 5: what a checkpointer saves, when, and under which thread.
Book: Chapter 5, section 5.3
Run: python -m pytest tests/test_ch05_more.py
"""
import operator
from typing import Annotated, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from ch05_helpers import Ticket, chain_graph, thread, ticket_graph

START_INPUT = {"customer": "Ana", "notes": []}


def history(graph, thread_id: str) -> list:
    return list(graph.get_state_history(thread(thread_id)))


def test_the_same_thread_continues_and_another_thread_starts_empty() -> None:
    graph = ticket_graph()
    graph.invoke({"customer": "Ana", "notes": ["one"]}, thread("ana"))
    second = graph.invoke({"notes": ["two"]}, thread("ana"))
    other = graph.invoke({"customer": "Ben", "notes": ["three"]}, thread("ben"))
    assert second["customer"] == "Ana" and second["notes"][0] == "one"
    assert other["notes"][0] == "three" and "one" not in other["notes"]


def test_one_invoke_saves_the_input_plus_one_checkpoint_per_super_step() -> None:
    for length in (1, 2, 3, 4):
        graph = chain_graph(length)
        graph.invoke(START_INPUT, thread("t"))
        steps = [saved.metadata["step"] for saved in history(graph, "t")]
        assert steps == list(range(length, -2, -1))  # newest first
        assert len(steps) == length + 2


def test_the_first_checkpoint_is_the_input_and_the_rest_come_from_the_loop() -> None:
    graph = ticket_graph()
    graph.invoke(START_INPUT, thread("t"))
    saved = list(reversed(history(graph, "t")))
    assert [s.metadata["source"] for s in saved] == ["input", "loop", "loop", "loop"]
    assert saved[0].next == ("__start__",) and saved[0].values == {"notes": []}
    assert saved[1].next == ("read",) and saved[3].next == ()
    assert set(saved[3].metadata) == {"source", "step", "parents"}


def test_the_super_step_of_a_node_is_the_step_of_the_checkpoint_after_it() -> None:
    seen: list[int] = []

    def watch(state: Ticket, config: RunnableConfig) -> dict:
        seen.append(config["metadata"]["langgraph_step"])
        return {}

    builder = StateGraph(Ticket)
    builder.add_node("watch", watch)
    builder.add_edge(START, "watch")
    builder.add_edge("watch", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    for _ in range(2):
        graph.invoke(START_INPUT, thread("t"))
    assert seen == [1, 4]  # step numbers continue on the same thread
    steps = [saved.metadata["step"] for saved in history(graph, "t")]
    assert steps == [4, 3, 2, 1, 0, -1]


def test_several_nodes_in_one_super_step_share_one_checkpoint() -> None:
    class Names(TypedDict):
        seen: Annotated[list, operator.add]

    builder = StateGraph(Names)
    for name in ["b", "c", "d"]:
        builder.add_node(name, lambda state, name=name: {"seen": [name]})
    builder.add_edge(START, "b")
    builder.add_edge(START, "c")
    builder.add_edge(["b", "c"], "d")
    builder.add_edge("d", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    graph.invoke({"seen": []}, thread("t"))
    saved = history(graph, "t")
    assert [s.metadata["step"] for s in saved] == [2, 1, 0, -1]
    assert saved[2].next == ("b", "c")


def test_a_second_invoke_runs_the_graph_from_start_on_the_saved_state() -> None:
    graph = ticket_graph()
    graph.invoke({"customer": "Ana", "notes": ["a"]}, thread("t"))
    second = graph.invoke({"customer": "Ben"}, thread("t"))
    assert second["customer"] == "Ben"  # a plain key in the input replaces
    assert second["notes"] == ["a", "read the email", "wrote a reply",
                               "read the email", "wrote a reply"]


def test_the_recursion_limit_counts_from_the_start_of_each_invoke() -> None:
    graph = ticket_graph()
    config = {**thread("t"), "recursion_limit": 3}
    for _ in range(3):  # steps climb to 10, the limit of 3 still holds
        graph.invoke(START_INPUT, config)
    assert graph.get_state(thread("t")).metadata["step"] == 10
