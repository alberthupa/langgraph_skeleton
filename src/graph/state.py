from typing_extensions import Annotated, TypedDict
from langgraph.graph.message import add_messages

# TODO: rewrite to Pydantic
# https://langchain-ai.github.io/langgraph/how-tos/state-model/


def merge_dicts(a: dict[str, any], b: dict[str, any]) -> dict[str, any]:
    return {**a, **b}


def overwrite(old_value, new_value) -> any:
    """Overwrite resolver that simply returns the new value."""
    return new_value


class AgentState(TypedDict):
    """
    Agent state definition
    """

    messages: Annotated[list, add_messages]
    user_data: Annotated[dict[str, any], merge_dicts]
    users_question_about_numeric_data: Annotated[str, overwrite]
    users_question_about_textual_data: Annotated[str, overwrite]
    dev_options: Annotated[dict[str, any], merge_dicts]
    clipboard: Annotated[
        dict[str, any], merge_dicts
    ]  # this is just an example of how to use data transfer through the workflow
