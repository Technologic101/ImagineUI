from langchain_core.messages import HumanMessage
from chains.design_rag import DesignRAG
from .workflow import create_graph, AgentState
from pathlib import Path

class DesignerAgent:
    def __init__(self, rag: DesignRAG) -> None:
        self.rag = rag
        self.workflow = create_graph(rag)
        self.state: AgentState = AgentState(
            messages=[],
            html_content=self._load_default_html(),
            style_requirements={},
            css_output=None
        )
    
    def _load_default_html(self) -> str:
        """Load default CSS Zen Garden HTML"""
        html_path = Path("data/csszengardenhtml.html")
        if html_path.exists():
            return html_path.read_text()
        return ""
    
    def set_html(self, html_content: str):
        """Set custom HTML content"""
        self.state["html_content"] = html_content
    
    async def process(self, message: str) -> str:
        """Process a message through the workflow"""
        try:
            self.state["messages"].append(HumanMessage(content=message))
            next_state = await self.workflow.ainvoke(self.state)
            self.state = next_state
            return self.state["messages"][-1].content
        except Exception as e:
            print(f"Error in process: {str(e)}")
            return "I encountered an error processing your message." 