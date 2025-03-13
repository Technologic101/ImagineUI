import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from chains.design_rag import DesignRAG

# Initialize components
design_rag = DesignRAG()

# System message focused on design analysis
SYSTEM_MESSAGE = """You are a helpful design assistant that finds and explains design examples.
For every user message, analyze their design preferences and requirements, considering:
1. Visual style and aesthetics
2. Color preferences and mood
3. Layout and structural needs
4. Key visual elements
5. Intended audience and user experience

First briefly explain how you understand their requirements, then show the closest match."""

@cl.on_chat_start
async def init():
    # Initialize LLM with callback handler inside the Chainlit context
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        streaming=True,
        callbacks=[cl.LangchainCallbackHandler()]
    )
    
    # Store the LLM in the user session
    cl.user_session.set("llm", llm)
    
    # init conversation history for each user
    cl.user_session.set("conversation_history", [
        SystemMessage(content=SYSTEM_MESSAGE)
    ])
    
    # Send welcome message
    await cl.Message(content="Welcome to ImagineUI! I'm here to help you design beautiful and functional user interfaces. What kind of design are you looking for?").send()

@cl.on_message
async def main(message: cl.Message):
    # Get the LLM from the user session
    llm = cl.user_session.get("llm")
    
    conversation_history = cl.user_session.get("conversation_history")
    # Add user message to history
    conversation_history.append(HumanMessage(content=message.content))
    
    # Get LLM's analysis of requirements
    analysis = await llm.ainvoke(conversation_history)
    
    # Get best design example based on full conversation
    designs = await design_rag.query_similar_designs(
        [msg.content for msg in conversation_history],
        num_examples=1
    )
    
    # Combine analysis with designs
    response = f"{analysis.content}\n\nHere is the best match from the zen garden:\n\n{designs}"
    
    # Add assistant's response to history
    conversation_history.append(SystemMessage(content=response))
    
    # Send response to user
    await cl.Message(content=response).send()

if __name__ == "__main__":
    cl.run() 