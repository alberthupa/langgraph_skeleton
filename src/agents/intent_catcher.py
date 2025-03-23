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
            "users_question_about_documentation": users_question_about_documentation,
            "users_question_about_database": users_question_about_numeric_data,
        }


def classify_intent(state: AgentState):
    """
    Tool node that classifies the user's intent based on their latest message.
    
    It determines whether the query relates to documentation, numeric data, both, or neither.
    
    Returns:
        Updated state with classification results
    """
    name_of_node = "intent_classifier"

    # Extract the latest user message from the state
    latest_messages = state["messages"]
    
    intent_classifier_system_prompt = fetch_system_prompt("intent_catcher")

    tool_identifying_scope = IntentCatchingTool()
    tools = [tool_identifying_scope]

    llm_client = create_vanilla_llm_client()
    llm_client_with_tools = llm_client.bind_tools(tools)

    # Only pass relevant context to the LLM
    dedicated_messages = [
        SystemMessage(content=intent_classifier_system_prompt)
    ] + latest_messages

    classification_response = llm_client_with_tools.invoke(dedicated_messages)

    if state.get("dev_options", {}).get("debug"):
        print(f"{name_of_node}: ", classification_response)

    has_tool_calls = (
        isinstance(classification_response.additional_kwargs, dict)
        and "tool_calls" in classification_response.additional_kwargs
    )

    if has_tool_calls:
        tool_response = json.loads(
            classification_response.additional_kwargs["tool_calls"][0]["function"]["arguments"]
        )
        
        # Extract and sanitize the intent classifications
        numeric_intent = tool_response.get("users_question_about_database")
        numeric_intent = None if numeric_intent in (None, "") else numeric_intent
        
        textual_intent = tool_response.get("users_question_about_documentation")
        textual_intent = None if textual_intent in (None, "") else textual_intent

        # Don't add a new message to the conversation, just return the classifications
        return {
            "messages": state["messages"],
            "users_question_about_numeric_data": numeric_intent,
            "users_question_about_textual_data": textual_intent,
        }
    else:
        # If no intent could be classified, return false for both intent flags
        return {
            "messages": state["messages"],
            "users_question_about_numeric_data": False,
            "users_question_about_textual_data": False,
        }


def get_user_input(state: AgentState):
    """
    Tool node that gets user input and adds it to the message history
    """
    user_input = input("User: ")
    input_message = HumanMessage(content=user_input)
    return {
        "messages": state["messages"] + [input_message],
        "users_question_about_numeric_data": None,  # Reset the intent flags
        "users_question_about_textual_data": None,  # Reset the intent flags
    }
