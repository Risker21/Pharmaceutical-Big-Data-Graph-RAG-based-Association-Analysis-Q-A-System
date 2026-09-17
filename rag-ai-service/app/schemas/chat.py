from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str
    content: str

class GraphEdge(BaseModel):
    from_node: str = Field(alias="from")
    to_node: str = Field(alias="to")
    rel: str
    
    class Config:
        populate_by_name = True

class RetrievalTrace(BaseModel):
    entities: List[str] = []
    graph_edges: List[Dict[str, str]] = []
    doc_chunks: List[str] = []
    contraindications: List[Dict[str, Any]] = []

class ChatStreamDone(BaseModel):
    status: str = "success"
    total_tokens: int = 0
    intent: Optional[str] = None
    response_ms: Optional[int] = None
