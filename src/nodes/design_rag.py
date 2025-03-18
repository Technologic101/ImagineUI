from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os

from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from pathlib import Path
import json
from typing import Dict, List, Optional
from langchain_core.documents import Document

class DesignRAG:
    def __init__(self):
        # Get API keys from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set it in HuggingFace Spaces settings."
            )
        
        # Initialize embedding model with explicit API key
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=api_key
        )
        
        # Load design data and create vector store
        self.vector_store = self._create_vector_store()
        
        # Create retriever with tracing
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4},
            tags=["design_retriever"]  # Add tags for tracing
        )
        
        # Create LLM with tracing
        self.llm = ChatOpenAI(
            temperature=0.2,
            tags=["design_llm"]  # Add tags for tracing
        )
    
    def _create_vector_store(self) -> FAISS:
        """Create FAISS vector store from design metadata"""
        try:
            # Update path to look in data/designs
            designs_dir = Path(__file__).parent.parent / "data" / "designs"

            documents = []
            
            # Load all metadata files
            for design_dir in designs_dir.glob("**/metadata.json"):
                try:
                    print(f"Processing design: {design_dir.parent.name}")
                    with open(design_dir, "r") as f:
                        metadata = json.load(f)
                    
                    # Create document text from metadata with safe gets
                    text = f"""
                    Title: {metadata.get('title', 'Untitled')}
                    Author: {metadata.get('author', 'Unknown')}
                    Description: {metadata.get('description', {}).get('summary', 'No description available')}
                    Categories: {', '.join(metadata.get('categories', []))}
                    Visual Characteristics: {', '.join(metadata.get('visual_characteristics', []))}
                    Artistic Style: {metadata.get('artistic_context', 'None Provided').get('style_influences', "None specified")}
                    """

                    # Create Document object with minimal metadata
                    documents.append(
                        Document(
                            page_content=text.strip(),
                            metadata={
                                "id": metadata.get('id', 'unknown'),
                                "path": str(design_dir.parent),
                                "title": metadata.get('title', 'Untitled'),
                                "author": metadata.get('author', 'Unknown')
                            }
                        )
                    )
                except Exception as e:
                    print(f"Error processing design {design_dir.parent.name}: {str(e)}")
                    continue
            
            if not documents:
                print("Warning: No valid design documents found")
                # Create empty vector store with a placeholder document
                return FAISS.from_documents(
                    [Document(page_content="No designs available", metadata={"id": "placeholder"})],
                    self.embeddings
                )
            
            print(f"Loaded {len(documents)} design documents")
            # Create and return vector store
            return FAISS.from_documents(documents, self.embeddings)
        except Exception as e:
            print(f"Error creating vector store: {str(e)}")
            raise
    
    async def query_similar_designs(self, conversation_history: List[str], num_examples: int = 1) -> str:
        """Find similar designs based on conversation history"""
        from langsmith import Client
        from langchain.callbacks.tracers import ConsoleCallbackHandler

        # Create LangSmith client
        client = Client()
        
        # Create query generation prompt with tracing
        query_prompt = ChatPromptTemplate.from_template(
            """Based on this conversation history:
            {conversation}
            Extract the key design requirements and create a search query to find similar designs.
            Focus on:
            1. Visual style and aesthetics mentioned
            2. Design categories and themes discussed
            3. Key visual characteristics requested
            4. Overall mood and impact desired
            5. Any specific preferences or constraints
            Return only the search query text, no additional explanation or analysis."""
        ).with_config(tags=["query_generation"])

        # Format conversation history
        conversation_text = "\n".join([
            f"{'User' if i % 2 == 0 else 'Assistant'}: {msg}"
            for i, msg in enumerate(conversation_history)
        ])
        
        # Generate optimized search query with tracing
        query_response = await self.llm.ainvoke(
            query_prompt.format(
                conversation=conversation_text
            )
        )
        
        print(f"Generated query: {query_response.content}")
        
        # Get relevant documents with tracing
        docs = self.retriever.get_relevant_documents(
            query_response.content, 
            k=num_examples,
            callbacks=[ConsoleCallbackHandler()]
        )
        
        # Format examples with improved readability
        examples = []
        for doc in docs:
            design_id = doc.metadata.get("id", "unknown")
            title = doc.metadata.get("title", "Untitled")
            author = doc.metadata.get("author", "Unknown")
            
            # Parse the content into sections
            content_lines = doc.page_content.strip().split("\n")
            sections = {}
            current_section = None
            
            for line in content_lines:
                line = line.strip()
                if not line:
                    continue
                if ":" in line:
                    current_section, value = line.split(":", 1)
                    sections[current_section.strip()] = value.strip()
            
            # Format the example with clear sections
            example = f"""
Design: {title}
By: {author}

Description:
{sections.get('Description', 'No description available')}

Categories:
{sections.get('Categories', 'No categories available')}

Visual Characteristics:
{sections.get('Visual Characteristics', 'No characteristics available')}

Artistic Style:
{sections.get('Artistic Style', 'No style information available')}

View at: https://csszengarden.com/{design_id}
"""
            examples.append(example.strip())
        
        return "\n\n" + "="*50 + "\n\n".join(examples) 