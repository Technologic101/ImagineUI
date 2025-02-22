from typing import Dict, List, Annotated, TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from chains.design_rag import DesignRAG
from langchain.prompts import ChatPromptTemplate
import chainlit as cl
import json

# Define state types
class AgentState(TypedDict):
    messages: List[BaseMessage]
    html_content: str
    style_requirements: Dict
    css_output: str | None

# Node functions
async def conversation_node(state: AgentState, rag: DesignRAG):
    """Handle conversation and requirement gathering"""
    # Get last message
    last_message = state["messages"][-1]
    
    if not isinstance(last_message, HumanMessage):
        return {"messages": state["messages"]}
    
    # Check for style requirements readiness
    if "!generate" in last_message.content.lower():
        # Extract style requirements from conversation
        requirements = await extract_requirements(state["messages"], rag)
        return {
            "messages": state["messages"],
            "style_requirements": requirements,
            "next": "generate_css"
        }
    
    # Normal conversation - get context and respond
    response = await rag.query(last_message.content)
    state["messages"].append(AIMessage(content=response))
    
    return {"messages": state["messages"]}

async def extract_requirements(
    messages: List[BaseMessage], 
    rag: DesignRAG
) -> Dict:
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
    
    # Get requirements through RAG system
    response = await rag.llm.ainvoke(prompt)
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
    
    # Store generated CSS
    state["css_output"] = response.content
    
    # Add completion message
    state["messages"].append(AIMessage(content="""I've generated the CSS based on your requirements. 
    Here's what I created:
    
    ```css
    {css}
    ```
    
    Would you like me to explain any part of the design or make any adjustments?
    """.format(css=response.content)))
    
    return state

def create_graph(rag: DesignRAG) -> StateGraph:
    """Create the workflow graph"""
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("conversation", lambda s: conversation_node(s, rag))
    workflow.add_node("generate_css", lambda s: generate_css_node(s, rag))
    
    # Add edges
    workflow.add_edge("conversation", "conversation")
    workflow.add_edge("conversation", "generate_css")
    workflow.add_edge("generate_css", END)
    
    # Set entry point
    workflow.set_entry_point("conversation")
    
    return workflow.compile() 