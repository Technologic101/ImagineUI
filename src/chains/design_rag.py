from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from pathlib import Path
import json
from typing import Dict, List, Optional
from langchain_core.documents import Document

class DesignRAG:
    def __init__(self):
        # Initialize embedding model
        self.embeddings = OpenAIEmbeddings()
        
        # Load design data and create vector store
        self.vector_store = self._create_vector_store()
        
        # Create retriever
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Create LLM
        self.llm = ChatOpenAI(temperature=0.2)
    
    def _create_vector_store(self) -> FAISS:
        """Create FAISS vector store from design metadata"""
        try:
            # Update path to look in data/designs
            designs_dir = Path("data/designs")
            
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
                    css_path = design_dir.parent / "style.css"
                    if css_path.exists():
                        with open(css_path, "r") as f:
                            css = f.read()
                        text += f"\nCSS:\n{css}"
                    
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
            
            # Create and return vector store
            return FAISS.from_documents(documents, self.embeddings)
        except Exception as e:
            print(f"Error creating vector store: {str(e)}")
            raise
    
    async def query_similar_designs(self, requirements: Dict) -> str:
        """Find similar designs based on requirements"""
        # Create search query from requirements
        query = f"""
        Style: {requirements['style_description']}
        Elements: {', '.join(requirements['key_elements'])}
        Colors: {requirements['color_scheme']}
        Layout: {requirements['layout_preferences']}
        Mood: {requirements['mood']}
        """
        
        # Get similar documents
        docs = await self.retriever.get_relevant_documents(query)
        
        # Format examples
        examples = []
        for doc in docs:
            examples.append(f"Example Design:\n{doc.page_content}\n")
        
        return "\n".join(examples) 