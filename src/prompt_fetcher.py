import os

path_to_prompts = os.path.join("src", "prompts")


def fetch_system_prompt(agent_name):
    if agent_name == "intent_catcher":
        with open(
            os.path.join(path_to_prompts, f"{agent_name}_system_prompt.txt"), "r"
        ) as f:
            system_prompt = f.read()

    return system_prompt


def fetch_scope_of_data_for_retrieval():
    with open(
        os.path.join(path_to_prompts, "scope_of_data_for_retrieval.txt"), "r"
    ) as f:
        scope_of_data_for_retrieval = f.read()

    return scope_of_data_for_retrieval


def fetch_text_scope_of_data_for_retrieval():
    with open(
        os.path.join(path_to_prompts, "text_scope_of_data_for_retrieval.txt"), "r"
    ) as f:
        scope_of_data_for_retrieval = f.read()

    return scope_of_data_for_retrieval


def fetch_numeric_scope_of_data_for_retrieval():
    with open(
        os.path.join(path_to_prompts, "numeric_scope_of_data_for_retrieval.txt"), "r"
    ) as f:
        scope_of_data_for_retrieval = f.read()

    return scope_of_data_for_retrieval
