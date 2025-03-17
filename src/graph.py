from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolInvoker
from nodes.designer import DesignerNode
from langchain.tools.render import format_tool_to_openai_function

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

def create_graph():
    # Initialize nodes
    designer = DesignerNode()
    
    # Create graph
    graph = StateGraph(State)
    
    # Add designer node
    graph.add_node("designer", designer)
    
    # Create tool invoker node with designer's tools
    tools = designer.get_available_tools()
    tool_executor = ToolInvoker(tools=tools)
    graph.add_node("tools", tool_executor)
    
    # Add edges
    graph.add_edge(START, "designer")
    
    # Add conditional edges based on tool calls
    graph.add_conditional_edges(
        "designer",
        lambda state: "tools" if state["messages"][-1].get("tool_calls") else END,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # After tool execution, return to designer
    graph.add_edge("tools", "designer")
    
    return graph.compile()

# Create the graph
graph = create_graph()


