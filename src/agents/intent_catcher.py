import json
from typing import Dict, Type, ClassVar
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.graph.state import AgentState
from src.llm_clients import create_vanilla_llm_client
from src.prompt_fetcher import (
    fetch_system_prompt,
    fetch_text_scope_of_data_for_retrieval,
    fetch_numeric_scope_of_data_for_retrieval,
    fetch_scope_of_data_for_retrieval,
)


class DoubleIntentCatchingInput(BaseModel):
    """
    Pydantic definition of the input schema for the IntentCatchingTool
    """

    textual_scope_of_data: ClassVar[str] = fetch_text_scope_of_data_for_retrieval()
    numeric_scope_of_data: ClassVar[str] = fetch_numeric_scope_of_data_for_retrieval()

    users_question_about_documentation: str = Field(
        description=f"summary of users question about text documentation of IT policies covering following scope: {textual_scope_of_data}"
    )

    users_question_about_numeric_data: str = Field(
        description=f"summary of users question about numeric data and reports about IT applications from sql database covering following scope: {numeric_scope_of_data}"
    )


class IntentCatchingTool(BaseTool):
    """
    Langchain BaseTool instance which is used (binded) to LLM client
    """

    name: str = "users_question_about_applications"
    description: str = """Identifies what the user wants to know about these IT applications, 
                       their data and policy documentation"""
    args_schema: Type[BaseModel] = DoubleIntentCatchingInput

    def _run(
        self,
        users_question_about_documentation: str,
        users_question_about_numeric_data: str,
    ) -> Dict[str, str]:
        scope_of_data_for_retrieval = fetch_scope_of_data_for_retrieval()
        f"""Use the tool only if a user asks a question that is at least a bit related to this scope: {scope_of_data_for_retrieval}"""
        return {
            # "users_question_about_applications": scope_of_knowledge_requested_by_user,
            "users_question_about_documentation": users_question_about_documentation,
            "users_question_about_database": users_question_about_numeric_data,
        }


def intent_catcher(state: AgentState):
    """
    This agent gets user input and:
    - if there is reasonable scope of knowledge requested by user, it returns tools
    - if there is no reasonable scope of knowledge requested by user, it returns message

    In worflow it requires functions: collect_input_for_intent_catching and should_continue_intent_catching
    and conditional edge

    """

    name_of_agent = "intent_catcher"

    intent_catcher_system_message = fetch_system_prompt(name_of_agent)

    tool_identifyng_scope_of_knowledge = IntentCatchingTool()
    tools = [tool_identifyng_scope_of_knowledge]

    llm_client = create_vanilla_llm_client()
    llm_client_with_tools = llm_client.bind_tools(tools)

    dedicated_messages_for_agent = [
        SystemMessage(intent_catcher_system_message)
    ] + state["messages"]

    agent_response = llm_client_with_tools.invoke(dedicated_messages_for_agent)

    if state.get("dev_options", {}).get("debug"):
        print(f"{name_of_agent}: ", agent_response)

    has_tool_calls = (
        isinstance(agent_response.additional_kwargs, dict)
        and "tool_calls" in agent_response.additional_kwargs
    )

    if has_tool_calls:
        ai_tool_response = json.loads(
            agent_response.additional_kwargs["tool_calls"][0]["function"]["arguments"]
        )
        ai_tool_message_numeric = ai_tool_response.get("users_question_about_database")
        ai_tool_message_numeric = (
            None if ai_tool_message_numeric in (None, "") else ai_tool_message_numeric
        )
        ai_tool_message_textual = ai_tool_response.get(
            "users_question_about_documentation"
        )
        ai_tool_message_textual = (
            None if ai_tool_message_textual in (None, "") else ai_tool_message_textual
        )

        return {
            "messages": state["messages"],
            "users_question_about_numeric_data": ai_tool_message_numeric,
            "users_question_about_textual_data": ai_tool_message_textual,
        }

    else:
        message = AIMessage(
            agent_name=name_of_agent,
            content=agent_response.content,
        )

        return {
            "messages": state["messages"] + [message],
            "users_question_about_numeric_data": False,
            "users_question_about_textual_data": False,
        }


def intent_catcher_input(state: AgentState):
    """
    this is a technical side function which just collects user input regarding users intent
    """
    user_input = input("User: ")
    input_message = HumanMessage(content=user_input)
    return {
        "messages": state["messages"] + [input_message],
        "users_question_about_numeric_data": None,  # Reset the intent flag,
        "users_question_about_textual_data": None,  # Reset the intent flag
    }
