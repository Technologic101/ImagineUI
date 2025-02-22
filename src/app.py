import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage
from chains.design_rag import DesignRAG
from agents.designer import DesignerAgent

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    # Initialize RAG system
    design_rag = DesignRAG()
    # Initialize designer agent
    designer = DesignerAgent(rag=design_rag)
    
    # Store in user session
    cl.user_session.set("designer", designer)

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    designer = cl.user_session.get("designer")
    
    # Process message through designer agent
    response = await designer.process(message.content)
    
    # Send response
    await cl.Message(content=response).send() 