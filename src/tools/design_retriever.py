from typing import Dict, Optional
from langchain.tools import BaseTool
from chains.design_rag import DesignRAG
from pydantic import Field
import json

class DesignRetrieverTool(BaseTool):
    """Tool for retrieving similar designs based on requirements."""
    
    name: str = "design_retriever"
    description: str = "Retrieves similar designs based on style requirements"
    rag: DesignRAG = Field(description="Design RAG system for retrieving similar designs")
    
    def __init__(self, rag: DesignRAG):
        """Initialize the tool with a DesignRAG instance."""
        super().__init__(rag=rag)
    
    def _run(self, requirements: Dict, num_examples: int = 3) -> str:
        """Sync version - not used but required by BaseTool"""
        raise NotImplementedError("Use async version")
    
    async def _arun(self, requirements: Dict, num_examples: int = 3) -> str:
        """Retrieve similar designs based on requirements"""
        print(f"Retrieving {num_examples} similar designs")
        return await self.rag.query_similar_designs(requirements, num_examples)