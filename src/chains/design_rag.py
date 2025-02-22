from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from pathlib import Path
import json
from typing import Dict

class DesignRAG:
    def __init__(self):
        # Initialize embedding model
        self.embeddings = OpenAIEmbeddings()
        
        # Load design data and create vector store
        self.vector_store = self._create_vector_store()
        
        # Create retriever
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        # Create LLM
        self.llm = ChatOpenAI(temperature=0.7)
        
        # Create the RAG chain
        self.chain = self._create_chain()
    
    def _create_vector_store(self):
        """Create FAISS vector store from design metadata"""
        designs_dir = Path("designs")
        documents = []
        
        # Load all metadata files
        for design_dir in designs_dir.glob("**/metadata.json"):
            with open(design_dir, "r") as f:
                metadata = json.load(f)
                
            # Create document text from metadata
            text = f"""
            Design {metadata['id']}:
            Description: {metadata.get('description', '')}
            Categories: {', '.join(metadata.get('categories', []))}
            Visual Characteristics: {', '.join(metadata.get('visual_characteristics', []))}
            """
            
            # Load associated CSS
            css_path = design_dir.parent / "style.css"
            if css_path.exists():
                with open(css_path, "r") as f:
                    css = f.read()
                text += f"\nCSS:\n{css}"
            
            documents.append({
                "page_content": text,
                "metadata": {
                    "id": metadata["id"],
                    "url": metadata.get("url", ""),
                }
            })
        
        # Create and return vector store
        return FAISS.from_documents(documents, self.embeddings)
    
    def _create_chain(self):
        """Create the RAG processing chain"""
        # Define prompt template
        template = """You are a design assistant helping to find and adapt CSS Zen Garden designs.
        Use the following similar designs to inform your response:
        
        {context}
        
        Based on these examples, help the user with their request:
        {question}
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Create and return chain
        chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain
    
    async def query(self, question: str) -> str:
        """Process a query through the RAG system"""
        return await self.chain.ainvoke(question)
    
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
        docs = self.retriever.get_relevant_documents(query)
        
        # Format examples
        examples = []
        for doc in docs:
            examples.append(f"Example Design:\n{doc.page_content}\n")
        
        return "\n".join(examples) 