# Langgraph Skeleton Code 

## Contents
- [Introduction](#introduction)
- [Dir structure](#dir-structure)
- [How to run the code](#how-to-run-the-code)
- [App body: State and workflow](#app-body-state-and-workflow)
  - [App state](#app-state)
  - [App workflow](#app-workflow)
- [LLM clients](#llm-clients)
- [Prompt fetcher](#prompt-fetcher)
- [Agents](#agents)


## Introduction
This is the skeleton Langgraph project build for the project Scaled Stewardship.
It is intended to be an initial code repository for project development.
As of 2025-01-20 it is pure Langgraph withouth any integration (neither front-end nor deployment, cloud environment and so on). Although this is generic code, its supposed to support features existing in code provided by the client.

## Dir structure
```
.
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── run.py
└── src/
    ├── agents/
    │   ├── intent_catcher.py
    │   ├── vanilla_agent_a.py
    │   └── vanilla_agent_b.py
    ├── auxiliary_code_snippets/
    │   └── databricks/
    │       └── output_message_catcher_for_stream
    ├── graph/
    │   ├── state.py
    │   └── workflow.py
    ├── llm_clients.py
    ├── prompt_fetcher.py
    └── prompts/
        ├── intent_catcher_system_prompt.txt
        ├── numeric_scope_of_data_for_retrieval.txt 
        ├── scope_of_data_for_retrieval.txt
        └── text_scope_of_data_for_retrieval.txt
```

## How to run the code.

### .env
First you have to populate .env file with:
```
OPENAI_API_VERSION=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
```

### run.py
File run.py has everything to run files from source (SRC dir).
It takes 2 parameters and allows for two types of options.

First, it can run in static mode or interactive / stream mode.
If you want to run it in interactive / stream mode add ***-i*** as in ***run.py -i***. If you want to run in static mode, do not add this param.

Running in interactive mode allows you to run any messages. Running in static mode has a hardcoded input message.

There is also -d, that is debug mode which adds some verbosity (to be coninued).

-----

By default run.py runs simple workflow, but there is also prepared another workflow designed for intent catching.


## App body: State and workflow.

### App state 
App state is in the file src/graph/state and has main class:

```python
class AgentState(TypedDict):
    """
    this collects all state placeholders for agents
    """
    messages: Annotated[list, add_messages]
    user_data: Annotated[dict[str, any], merge_dicts] # this is plcaeholder for session and user data
    users_question_about_numeric_data: Annotated[str, overwrite] # this holds user intende question for numeric data
    users_question_about_textual_data: Annotated[str, overwrite] # this holds user intende question for text data
    dev_options: Annotated[dict[str, any], merge_dicts] # this is supposed to help verbose / debug mode
    clipboard: Annotated[ # this is just a dummy dict, an example 
        dict[str, any], merge_dicts
    ] 
```

### App workflow

Workflow is the apps logic. Currently in the file src/graph/workflow.py there are 2 workflows.


First workflow is a simple one, just for understanding how the logic works. It passess conversation from user to one agent, then another and then finishes it. If run in static workflow this will simply run everything once. If run in stream mode, it allows for infinite conversation.


There is also prepared workflow designed for intent catching. It uses an agent ***intent_catcher*** as long as it catched the intent. This intent catching should be developped more thouroughly along the project. If you want to use it, you have to put its name into **run.py** file in the INIT GRAPH section.


## LLM clients
In file src/llm_clients there is currently simple llm client:

```python 
def create_vanilla_llm_client(deployment_name="gpt-4o-mini"):
    llm = AzureChatOpenAI(
        deployment_name=deployment_name,
    )

    return llm
```

This will be developped according to client needs.

## Prompt fetcher
In file src/prompt_fetcher.py there are basic functions to fetch text variables used in prompts which are stored in dir src/prompts


## Agents
Dir src/agents holds code for agents used in the workflow.


* ***vanilla_agent_a*** is an agent which does only one thing: it makes llm answer message list and pass it further.
* ***vanilla_agent_b*** is a sample agent which does nothig. It simply return state.
* ***intent_catcher*** is an agent which collects user intent. This is the beginning of the agent that will understand and rephrase users questions so that they will be passed to RAG agents. This in used only in the create_intent_catching_workflow().

