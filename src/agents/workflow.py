from typing import Dict, List, Annotated, TypedDict, Callable, Any
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from chains.design_rag import DesignRAG
from langchain.prompts import ChatPromptTemplate
import chainlit as cl
import json
from langchain_openai import ChatOpenAI

# Define state types
class AgentState(TypedDict):
    messages: List[BaseMessage]
    html_content: str
    style_requirements: Dict
    css_output: str | None

# At the top level
llm = ChatOpenAI(temperature=0.2)

def should_end(state: AgentState) -> str:
    """Determine if the conversation should end"""
    if state["messages"] and isinstance(state["messages"][-1], HumanMessage):
        if "!done" in state["messages"][-1].content.lower():
            return "end"
    return "conversation"

async def conversation_node(state: AgentState) -> AgentState:
    """Handle conversation and requirement gathering"""
    last_message = state["messages"][-1]
    print("last message received")
    print(last_message)
    
    if not isinstance(last_message, HumanMessage):
        return state
    
    if "!generate" in last_message.content.lower():
        requirements = await extract_requirements(state["messages"])
        await cl.Message("I'll generate CSS based on your requirements...").send()
        return AgentState(
            messages=state["messages"],
            html_content=state["html_content"],
            style_requirements=requirements,
            css_output=state["css_output"]
        )
    
    # Normal conversation - just acknowledge and guide
    response = "I understand. Tell me more about the design you're looking for, or type !generate when you're ready to create the CSS."
    await cl.Message(content=response).send()
    
    return AgentState(
        messages=[*state["messages"], AIMessage(content=response)],
        html_content=state["html_content"],
        style_requirements=state.get("style_requirements", {}),
        css_output=state.get("css_output")
    )

async def extract_requirements(messages: List[BaseMessage]) -> Dict:
    """Extract style requirements from conversation history"""
    # Combine messages into context
    context = "\n".join([
        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
        for m in messages
    ])
    
    # Create extraction prompt
    prompt = f"""Based on this conversation, extract the key style requirements:
    
    {context}
    
    Provide the requirements in this JSON format:
    {{
        "style_description": "Brief description of desired style",
        "key_elements": ["list", "of", "important", "visual", "elements"],
        "color_scheme": "Description of colors",
        "layout_preferences": "Any specific layout requirements",
        "mood": "Desired emotional impact"
    }}
    """
    
    # Get requirements through LLM
    response = await llm.ainvoke(prompt)
    return json.loads(response.content)

async def generate_css_node(state: AgentState, rag: DesignRAG) -> AgentState:
    """Generate CSS based on requirements"""
    # Get similar designs based on requirements
    similar_designs = await rag.query_similar_designs(state["style_requirements"])
    
    # Create the generation prompt
    prompt = ChatPromptTemplate.from_template("""You are an expert CSS designer creating a style for the following HTML structure:
    
    HTML Structure:
    {html_content}
    
    Style Requirements:
    {requirements}
    
    Similar Design Examples:
    {examples}
    
    Generate a complete CSS file that:
    1. Implements the requested style requirements
    2. Uses modern CSS features appropriately
    3. Creates a cohesive and polished design
    4. Includes comments explaining key style decisions
    
    Respond only with the CSS code, starting with a comment block describing the design approach.
    """)
    
    # Format requirements for prompt
    requirements_text = json.dumps(state["style_requirements"], indent=2)
    
    # Generate CSS
    response = await rag.llm.ainvoke(
        prompt.format(
            html_content=state["html_content"],
            requirements=requirements_text,
            examples=similar_designs
        )
    )
    
    css_message = f"""I've generated the CSS based on your requirements. 
    Here's what I created:
    
    ```css
    {response.content}
    ```
    
    Would you like me to explain any part of the design or make any adjustments?
    Type !done when you're satisfied with the result."""
    
    await cl.Message(content=css_message).send()
    
    return AgentState(
        messages=[*state["messages"], AIMessage(content=css_message)],
        html_content=state["html_content"],
        style_requirements=state["style_requirements"],
        css_output=response.content
    )

def create_graph(rag: DesignRAG) -> StateGraph:
    """Create the workflow graph"""
    workflow = StateGraph(AgentState)
    
    # Add nodes directly
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("generate_css", lambda s: generate_css_node(s, rag))
    
    # Add edges
    workflow.add_conditional_edges(
        "conversation",
        should_end,  # Use our existing should_end function
        {
            "conversation": "conversation",
            "generate_css": "generate_css",
            "end": END
        }
    )
    workflow.add_edge("generate_css", "conversation")
    
    workflow.set_entry_point("conversation")
    return workflow.compile() 