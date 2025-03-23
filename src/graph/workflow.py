from langgraph.graph import START, StateGraph
from src.graph.state import AgentState
from src.agents.intent_catcher import intent_catcher, intent_catcher_input
from src.agents.vanilla_agent_a import vanilla_agent_a
from src.agents.vanilla_agent_b import vanilla_agent_b


def create_workflow():
    """
    This is a sample workflow which simply passes conversation from one agent to another:
    agent a creates a reply
    agent b does nothing
    """

    workflow = StateGraph(AgentState)
    workflow.add_edge(START, "vanilla_agent_a")
    workflow.add_node("vanilla_agent_a", vanilla_agent_a)
    workflow.add_node("vanilla_agent_b", vanilla_agent_b)
    workflow.add_edge("vanilla_agent_a", "vanilla_agent_b")
    return workflow


def create_intent_catching_workflow():
    """
    create_intent_catching_workflow
    This workflow aims at catching the intent of the user.
    If it does it passes conversation to vanilla_agent_a
    """

    def should_continue_intent_catching(state: AgentState):
        """
        this is a function for conditional edge which decides if we should continue intent catching
        """
        return (
            "vanilla_agent_a"
            # if state["data_intent_summarization"]
            if state.get("users_question_about_numeric_data")
            or state.get("users_question_about_textual_data")
            else "intent_catcher_input"
        )

    workflow = StateGraph(AgentState)

    workflow.add_node("intent_catcher", intent_catcher)
    workflow.add_node("intent_catcher_input", intent_catcher_input)
    workflow.add_node("vanilla_agent_a", vanilla_agent_a)

    workflow.add_edge(START, "intent_catcher")
    workflow.add_conditional_edges(
        "intent_catcher",
        should_continue_intent_catching,
        {
            "vanilla_agent_a": "vanilla_agent_a",
            "intent_catcher_input": "intent_catcher_input",
        },
    )
    workflow.add_edge("intent_catcher_input", "intent_catcher")

    return workflow
