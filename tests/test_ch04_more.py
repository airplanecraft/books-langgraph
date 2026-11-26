"""More tests for chapter 4: the loop, tools_condition, the limit and two wiring mistakes.
Book: Chapter 4, section 4.10
Run: python -m pytest tests/test_ch04_more.py
"""
import pytest
from langgraph.errors import GraphRecursionError
from langgraph.graph import END
from langgraph.prebuilt import tools_condition

from ch04_helpers import QUESTION, RUNS, agent, kinds, request
from common import ask_for, say


def asks(order_id: str, call_id: str = "c1"):
    return ask_for("lookup_order", {"order_id": order_id}, call_id)


def test_the_loop_grows_the_message_list_two_at_a_time() -> None:
    graph, _ = agent([asks("A17", "c1"), asks("B42", "c2"), say("Done.")])
    assert kinds(graph.invoke(QUESTION)) == [
        "human", "ai", "tool", "ai", "tool", "ai"]


def test_tools_condition_gives_the_same_run_as_the_own_route() -> None:
    script = [asks("A17"), say("Done.")]
    own, _ = agent(list(script))
    ready, _ = agent(list(script), router=tools_condition)
    first, second = own.invoke(QUESTION), ready.invoke(QUESTION)
    assert [m.content for m in first["messages"]] == [
        m.content for m in second["messages"]]
    assert tools_condition({"messages": [request("x", {})]}) == "tools"
    assert tools_condition({"messages": [say("hi")]}) == END
    with pytest.raises(ValueError):
        tools_condition({"messages": []})


def test_a_loop_that_never_ends_stops_at_the_recursion_limit() -> None:
    RUNS.clear()
    graph, model = agent([asks("B42", f"c{n}") for n in range(10)],
                         router=tools_condition)
    with pytest.raises(GraphRecursionError):
        graph.invoke(QUESTION, config={"recursion_limit": 6})
    assert model.replies_used == 3
    assert RUNS == ["B42", "B42", "B42"]  # three tool runs


def test_a_round_trip_needs_a_limit_of_four() -> None:
    graph, _ = agent([asks("B42"), say("Done.")])
    done = graph.invoke(QUESTION, config={"recursion_limit": 4})
    assert len(done["messages"]) == 4
    graph, _ = agent([asks("B42"), say("Done.")])
    with pytest.raises(GraphRecursionError):
        graph.invoke(QUESTION, config={"recursion_limit": 3})


def test_without_an_edge_back_the_run_ends_after_the_tool_message() -> None:
    graph, _ = agent([asks("B42"), say("Done.")], router=tools_condition,
                     edge_back=False)
    assert kinds(graph.invoke(QUESTION)) == ["human", "ai", "tool"]


def test_a_tool_node_with_another_name_fails_to_compile() -> None:
    script = [asks("B42"), say("Done.")]
    with pytest.raises(ValueError):
        agent(script, router=tools_condition, tool_name="runner")
    graph, _ = agent(script, router=tools_condition, tool_name="runner",
                     path_map={"tools": "runner", "__end__": END})
    assert kinds(graph.invoke(QUESTION)) == ["human", "ai", "tool", "ai"]


def test_a_limit_of_ten_allows_four_rounds_and_the_answer() -> None:
    def rounds(count: int):
        script = [asks("B42", f"c{n}") for n in range(count)] + [say("Done.")]
        graph, _ = agent(script, router=tools_condition)
        return graph.invoke(QUESTION, config={"recursion_limit": 10})

    assert len(rounds(4)["messages"]) == 10  # 9 node runs, limit 10
    with pytest.raises(GraphRecursionError):
        rounds(5)
