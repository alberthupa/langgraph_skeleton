from langchain_core.messages import AIMessage
from src.graph.state import AgentState
from src.llm_clients import create_vanilla_llm_client


def vanilla_agent_a(state: AgentState):
    """
    This is a sample agent which answers users question
    """

    name_of_agent = "vanilla_agent_a"
    llm_client = create_vanilla_llm_client()
    ai_response = llm_client.invoke(state["messages"])

    if state.get("dev_options", {}).get("debug"):
        print("vanilla_agent_a: ", ai_response)

    message = AIMessage(
        agent_name=name_of_agent,
        content=ai_response.content,
        # lines below are standrd fields of Response object
        # response_metadata=ai_response.response_metadata,
        # additional_kwargs=ai_response.additional_kwargs,
        # id=ai_response.id,
        # usage_metadata=ai_response.usage_metadata,
    )

    return {
        "messages": state["messages"] + [message],
        # showcase how to change session metatadata
        # "clipboard": {**state["clipboard"], **{"d": 4}},
    }
