from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from tools.design_retriever import design_retriever_tool


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

model = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)

tools = [
    design_retriever_tool
]

model_with_tools = model.bind_tools(tools)

graph = create_react_agent(model_with_tools, tools=tools)

