from typing import Dict, List
from anthropic import AsyncAnthropic
import json
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from nodes.design_rag import DesignRAG

class DesignerNode:
    """Main conversation node for discussing design requirements and retrieving examples"""
    
    def __init__(self):
        self.client = AsyncAnthropic()
        self.rag = DesignRAG()
        
        # Define the conversation prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert design assistant helping users find design inspiration.
            Your goal is to understand their design needs and requirements through conversation.
            
            Guidelines:
            1. Focus on understanding visual design requirements, not implementation
            2. Ask clarifying questions about style, mood, and visual elements
            3. When the user asks to see examples, use the retrieve_design_examples tool
            4. Track both must-have requirements and nice-to-have preferences
            5. When showing examples, explain how they match the requirements
            
            Available tools:
            - retrieve_design_examples: Find relevant design examples based on conversation
            
            When the user asks to see examples, ALWAYS use the retrieve_design_examples tool.
            Format tool calls using the exact function name and parameters.
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

    @tool()
    async def retrieve_design_examples(self, conversation: List[str], num_examples: int = 1) -> str:
        """
        Find and retrieve relevant design examples based on the conversation history.
        
        Args:
            conversation: List of conversation messages
            num_examples: Number of examples to retrieve (default: 1)
            
        Returns:
            String containing design examples and their details
        """
        return await self.rag.query_similar_designs(conversation, num_examples)

    def get_available_tools(self):
        """Return list of available tools"""
        return [self.retrieve_design_examples]

    async def __call__(self, state: Dict) -> Dict:
        """Process messages and manage design discussion"""
        messages = state.get("messages", [])
        
        # Convert messages to chat history format
        chat_history = []
        for msg in messages[:-1]:  # Exclude the last message which is the current input
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                chat_history.append(
                    HumanMessage(content=content) if role == "user" 
                    else AIMessage(content=content)
                )
            elif isinstance(msg, BaseMessage):
                chat_history.append(msg)
        
        # Get the current input message
        current_input = messages[-1].get("content") if isinstance(messages[-1], dict) else messages[-1].content
        
        # Get response from Claude
        response = await self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": self.prompt.format(
                    chat_history=chat_history,
                    input=current_input
                )
            }]
        )
        
        response_text = response.content[0].text
        
        # Check if response indicates need for examples
        should_retrieve = (
            "retrieve_design_examples" in response_text or
            any(phrase in current_input.lower() 
                for phrase in ["show example", "find design", "get example"])
        )
        
        if should_retrieve:
            # Create tool call message
            state["messages"].append({
                "role": "assistant",
                "content": response_text,
                "tool_calls": [{
                    "type": "function",
                    "function": {
                        "name": "retrieve_design_examples",
                        "arguments": json.dumps({
                            "conversation": [msg.get("content", msg) if isinstance(msg, dict) else msg 
                                          for msg in messages],
                            "num_examples": 1
                        })
                    }
                }]
            })
        else:
            # Regular response without tool calls
            state["messages"].append({
                "role": "assistant",
                "content": response_text
            })
        
        return state
