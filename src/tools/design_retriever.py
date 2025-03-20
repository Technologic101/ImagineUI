from nodes.design_rag import DesignRAG
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage

# this should be done at app level is used elsewhere
rag = DesignRAG()

async def design_retriever_tool(state: MessagesState, num_examples: int = 1):
    """
        Retrieves similar designs based on style requirements
        Name: query_similar_designs
    """
    
    result = await rag.query_similar_designs(state["messages"], num_examples)

    return SystemMessage(content=result)

