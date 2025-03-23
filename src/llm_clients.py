from langchain_openai import AzureChatOpenAI


def create_vanilla_llm_client(deployment_name="gpt-4o"):
    """
    gpt-4o-mini
    """
    llm = AzureChatOpenAI(
        deployment_name=deployment_name,
    )

    return llm
