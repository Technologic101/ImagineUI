import chainlit as cl
from chains.design_rag import DesignRAG
from agents.designer import DesignerAgent

# Initialize these once at module level
design_rag = DesignRAG()
designer = DesignerAgent(rag=design_rag)

@cl.on_chat_start
async def start() -> None:
    """Initialize the chat session"""
    # Store in user session
    cl.user_session.set("designer", designer)
    
    # Send welcome message
    await cl.Message(
        content="Welcome! I'm here to help you imagine a unique design. What style are you looking for?"
    ).send()

@cl.on_message
async def main(message: cl.Message) -> None:
    """Handle incoming messages"""
    designer = cl.user_session.get("designer")
    if designer is None:
        # Reinitialize if missing
        designer = DesignerAgent(rag=design_rag)
        cl.user_session.set("designer", designer)
    
    # Process message through designer agent
    response = await designer.process(message.content)
    
    # Send response
    await cl.Message(content=response).send() 