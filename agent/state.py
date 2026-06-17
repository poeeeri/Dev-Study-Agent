from langgraph.graph.message import add_messages
from typing import TypedDict, Dict, List, Any, Annotated, Optional


class AgentState(TypedDict):
    messages: Annotated[List[Dict[str, Any]], add_messages]
    # context for RAG and memory (i'll leave it that way for now)
    context: List[Dict[str, Any]]
    command: Optional[str]
    # if passed validation
    is_safe: Optional[bool]
    plan: List[str]
    files_to_read: Optional[list]
    tool_calls: Optional[list]
    tool_results: List[str]
    iteration: int # iteration counter