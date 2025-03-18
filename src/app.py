import chainlit as cl
from langchain_core.messages import HumanMessage, SystemMessage
from graph import graph

# System message focused on design analysis
SYSTEM_MESSAGE = """You are a helpful design assistant that finds and explains design examples.
For every user message, analyze their design preferences and requirements, considering:
1. Visual style and aesthetics
2. Color preferences and mood
3. Layout and structural needs
4. Key visual elements
5. Intended audience and user experience
"""

@cl.on_chat_start
async def init():
    # Store the graph in the user session
    cl.user_session.set("graph", graph)
    
    # Initialize conversation state with system message
    initial_state = {
        "messages": [SystemMessage(content=SYSTEM_MESSAGE)]
    }
    cl.user_session.set("state", initial_state)
    
    # Send welcome message
    await cl.Message(content="Welcome to ImagineUI! I'm here to help you design beautiful and functional user interfaces. What kind of design are you looking for?").send()

@cl.on_message
async def main(message: cl.Message):
    # Get the graph from the user session
    graph = cl.user_session.get("graph")
    
    # Get current state
    state = cl.user_session.get("state")
    
    # Add the new user message to the state
    state["messages"].append(HumanMessage(content=message.content))
    
    # Process message through the graph
    result = await graph.ainvoke(state)
    print("Here's the result: ", result)
    
    # Update state with the result
    state["messages"].extend(result["messages"])
    
    # Extract the last assistant message for display
    last_message = result["messages"][-1].content
    
    # Send response to user
    await cl.Message(content=last_message).send()

if __name__ == "__main__":
    cl.run()