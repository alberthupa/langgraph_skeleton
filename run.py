import argparse

from dotenv import load_dotenv
import uuid

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from src.graph.workflow import create_workflow


def parse_args():
    # PARSE ARGUMENTS
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Enable interactive mode"
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()
    return args


def main():
    load_dotenv(".env", override=True)

    # parse args for running this file
    args = parse_args()
    debug_mode = bool(args.debug)

    # SESSION METADATA
    # get some session_id for graph persistence
    conversation_id = uuid.uuid4()

    # get some user data (to be filled later)
    user_data = {
        "name": "John Doe",
        "persona": "data_analyst",
        "shortname": "John",
        "organization": "Acme Inc.",
    }

    # this is just an example of some additional context data
    clipboard = {
        "a": 1,
        "b": 2,
        "c": 3,
    }

    # INIT GRAPH
    checkpointer = MemorySaver()
    workflow = create_workflow()
    graph = workflow.compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": conversation_id}}

    # RUN GRAPH
    # run app in interactive loop mode
    if args.interactive:
        try:
            while True:
                user_input = input("User: ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break

                input_message = HumanMessage(content=user_input)
                for event in graph.stream(
                    {
                        "messages": [input_message],
                        "user_data": user_data,
                        "clipboard": clipboard,
                        "dev_options": {"debug": debug_mode},
                    },
                    config,
                    stream_mode="values",
                ):
                    # event["messages"][-1].pretty_print()
                    print(event)
        except Exception as e:
            print(e)

    # run one-off in static mode
    else:
        graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        # content="Hello",
                        content="which apps are iRisk compliant?"
                    )
                ],
                "user_data": user_data,
                "clipboard": clipboard,
                "dev_options": {"debug": debug_mode},
            },
            config=config,
        )


if __name__ == "__main__":
    main()
