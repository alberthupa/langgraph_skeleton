"""
In Databricks context our "agent" means a graph that handles outputs
This function below basically makes sure that in all scenarios the graph returns a simple string.
This will work in Sanbox App on Databricks
It works both for agent.invoke() and agent.stream() methods


from typing import Iterator, Dict, Any, List
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
    MessageLikeRepresentation,
)
from langchain_core.runnables import RunnableGenerator


# FIRST: Create a graph that will be used as an age
# compiled_graph = graph.compile()


def wrap_output(stream: Iterator[MessageLikeRepresentation]) -> Iterator[str]:

    # Processes a stream of messages and extracts relevant information based on the structure.

    # Args:
    #    stream: An iterator yielding message-like objects.

    # Yields:
    #    Strings representing extracted information from the messages.

    for event in stream:
        if isinstance(event, dict):
            if "messages" in event and isinstance(event["messages"], list):
                # SCENARIO: SIMPLE LIST
                for msg in event["messages"]:
                    if isinstance(msg, AIMessage):
                        yield msg.content
            elif all(
                isinstance(value, dict) and "messages" in value
                for value in event.values()
            ):
                # SCENARIO: LIST OF AGENTS
                longest_agent_messages: List[MessageLikeRepresentation] = []
                for agent_data in event.values():
                    if isinstance(agent_data, dict) and isinstance(
                        agent_data.get("messages"), list
                    ):
                        if len(agent_data["messages"]) > len(longest_agent_messages):
                            longest_agent_messages = agent_data["messages"]

                if longest_agent_messages:
                    last_message = longest_agent_messages[-1]
                    if isinstance(last_message, AIMessage):
                        yield last_message.content
        # Added handling for AIMessage directly - useful if .stream() directly returns AIMessage
        elif isinstance(event, AIMessage):
            yield event.content
        # Handle other cases if needed in the future, or simply ignore them by not yielding anything



# agent = compiled_graph | RunnableGenerator(wrap_output)


this is the context where the agent is used
for event in agent.stream({"messages": [HumanMessage(content="Hi, mate")]}):
    print(event, "---" * 20 + "\n")
"""
