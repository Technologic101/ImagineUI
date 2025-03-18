from nodes.design_rag import DesignRAG
from langgraph.graph import MessagesState

def design_retriever_tool(state: MessagesState, num_examples: int = 2):
    """
        Retrieves similar designs based on style requirements
        Name: query_similar_designs
    """
    return DesignRAG.query_similar_designs(state["messages"], num_examples)

