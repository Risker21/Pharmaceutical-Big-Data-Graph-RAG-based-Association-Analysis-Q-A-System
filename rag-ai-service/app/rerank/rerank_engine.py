from typing import Dict, Any

class RerankEngine:
    def rerank(self, retrieval_result: Dict[str, Any], query: str) -> Dict[str, Any]:
        # Filter duplicates and limit chunks
        chunks = retrieval_result.get("doc_chunks", [])
        retrieval_result["doc_chunks"] = chunks[:3]
        return retrieval_result
