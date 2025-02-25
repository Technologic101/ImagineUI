from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
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
        # Get API key from environment
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
        
        # Create retriever
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 1}
        )
        
        # Create LLM
        self.llm = ChatOpenAI(temperature=0.2)
    
    def _create_vector_store(self) -> FAISS:
        """Create FAISS vector store from design metadata"""
        try:
            # Update path to look in data/designs
            designs_dir = Path(__file__).parent.parent / "data" / "designs"

            documents = []
            
            # Load all metadata files
            for design_dir in designs_dir.glob("**/metadata.json"):
                try:
                    with open(design_dir, "r") as f:
                        metadata = json.load(f)
                    
                    # Create document text from metadata with safe gets
                    text = f"""
                    Design {metadata.get('id', 'unknown')}:
                    Description: {metadata.get('description', 'No description available')}
                    Categories: {', '.join(metadata.get('categories', []))}
                    Visual Characteristics: {', '.join(metadata.get('visual_characteristics', []))}
                    """
                    
                    # Load associated CSS
                    '''
                    css_path = design_dir.parent / "style.css"
                    if css_path.exists():
                        with open(css_path, "r") as f:
                            css = f.read()
                        text += f"\nCSS:\n{css}"
                    '''

                    # Create Document object with minimal metadata
                    documents.append(
                        Document(
                            page_content=text.strip(),
                            metadata={
                                "id": metadata.get('id', 'unknown'),
                                "path": str(design_dir.parent)
                            }
                        )
                    )
                except Exception as e:
                    print(f"Error processing design {design_dir}: {e}")
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
        """Find similar designs based on conversation history
        
        Args:
            conversation_history: List of conversation messages
            num_examples: Number of examples to retrieve
        """
        # Create query generation prompt
        query_prompt = ChatPromptTemplate.from_template("""Based on this conversation history:

        {conversation}

        Extract the key design requirements and create a search query to find similar designs.
        Focus on:
        1. Visual style and aesthetics mentioned
        2. Design categories and themes discussed
        3. Key visual characteristics requested
        4. Overall mood and impact desired
        5. Any specific preferences or constraints

        Return only the search query text, no additional explanation or analysis.""")
        
        # Format conversation history
        conversation_text = "\n".join([
            f"{'User' if i % 2 == 0 else 'Assistant'}: {msg}"
            for i, msg in enumerate(conversation_history)
        ])
        
        # Generate optimized search query
        query_response = await self.llm.ainvoke(
            query_prompt.format(
                conversation=conversation_text
            )
        )
        
        print(f"Generated query: {query_response.content}")
        
        # TODO: Update to use invoke
        docs = self.retriever.get_relevant_documents(
            query_response.content, 
            k=num_examples
        )
        
        # Format examples
        examples = []
        for doc in docs:
            # Extract key info
            design_id = doc.metadata.get("id", "unknown")
            content_lines = doc.page_content.strip().split("\n")
            
            # Format nicely
            examples.append(
                "\n".join(line.strip() for line in content_lines if line.strip()) +
                f"\nURL: https://csszengarden.com/{design_id}"
            )
        
        return "\n\n".join(examples) 