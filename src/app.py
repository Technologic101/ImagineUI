import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from chains.design_rag import DesignRAG

# Initialize components
design_rag = DesignRAG()
conversation_history = []

# System message focused on design analysis
SYSTEM_MESSAGE = """You are a helpful design assistant that finds and explains design examples.
For every user message, analyze their design preferences and requirements, considering:
1. Visual style and aesthetics
2. Color preferences and mood
3. Layout and structural needs
4. Key visual elements

First explain how you understand their requirements, then show relevant design examples."""

@cl.on_chat_start
async def init():
    # Initialize LLM with streaming
    global llm
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        streaming=True,
        callbacks=[cl.LangchainCallbackHandler()]
    )
    
    # Store system message
    conversation_history.append(SystemMessage(content=SYSTEM_MESSAGE))
    
    # Send welcome message
    await cl.Message(content="Hello! What kind of design are you looking for?").send()

@cl.on_message
async def main(message: cl.Message):
    # Add user message to history
    conversation_history.append(HumanMessage(content=message.content))
    
    # Get LLM's analysis of requirements
    analysis = await llm.ainvoke(conversation_history)
    
    # Get design examples based on full conversation
    designs = await design_rag.query_similar_designs(
        [msg.content for msg in conversation_history],
        num_examples=3
    )
    
    # Combine analysis with designs
    response = f"{analysis.content}\n\nHere are some relevant designs:\n\n{designs}"
    
    # Add assistant's response to history
    conversation_history.append(SystemMessage(content=response))
    
    # Send response to user
    await cl.Message(content=response).send()

if __name__ == "__main__":
    cl.run() 