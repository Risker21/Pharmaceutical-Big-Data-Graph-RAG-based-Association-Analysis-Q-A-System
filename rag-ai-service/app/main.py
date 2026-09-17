import json
import os
import time
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from loguru import logger

from app.schemas.chat import RetrievalTrace, ChatStreamDone
from app.ner.entity_extractor import extract_entities, classify_intent
from app.retrieval.hybrid_retriever import HybridRetriever
from app.rerank.rerank_engine import RerankEngine
from app.prompt.prompt_assembler import PromptAssembler
from app.generators.mock_generator import MockLLMGenerator

app = FastAPI(title="MedGraphRAG AI Engine", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

retriever = HybridRetriever()
reranker = RerankEngine()
assembler = PromptAssembler()
generator = MockLLMGenerator()

# Chat analysis logging store
chat_stats_history = [
    {"day": "2026-09-10", "sessions": 120, "messages": 450, "tokens": 156000},
    {"day": "2026-09-11", "sessions": 145, "messages": 520, "tokens": 182000},
    {"day": "2026-09-12", "sessions": 160, "messages": 610, "tokens": 215000},
    {"day": "2026-09-13", "sessions": 190, "messages": 730, "tokens": 258000},
    {"day": "2026-09-14", "sessions": 210, "messages": 820, "tokens": 290000},
    {"day": "2026-09-15", "sessions": 245, "messages": 950, "tokens": 334000},
]

@app.get("/health")
async def health():
    return {"status": "ok", "service": "rag-ai-service", "timestamp": int(time.time())}

@app.get("/api/v1/chat/stream")
async def chat_stream(
    query: str = Query(..., description="用户咨询问题"),
    sessionId: Optional[str] = Query(None, description="会话ID")
):
    start_ts = time.time()
    entities = extract_entities(query)
    intent = classify_intent(query, entities)
    
    # 1. Hybrid Retrieval
    raw_context = retriever.retrieve(query, entities, intent)
    
    # 2. Rerank
    context = reranker.rerank(raw_context, query)
    
    async def event_generator():
        # Event 1: trace
        trace_data = {
            "entities": context.get("entities", []),
            "graph_edges": context.get("graph_edges", []),
            "doc_chunks": context.get("doc_chunks", []),
            "contraindications": context.get("contraindications", [])
        }
        yield f"event: trace\ndata: {json.dumps(trace_data, ensure_ascii=False)}\n\n"
        
        # Event 2: token streams
        token_count = 0
        async for token in generator.stream_generate(query, context):
            token_count += len(token)
            data_frame = {"delta": token}
            yield f"event: token\ndata: {json.dumps(data_frame, ensure_ascii=False)}\n\n"
            
        # Event 3: done
        elapsed_ms = int((time.time() - start_ts) * 1000)
        done_frame = {
            "status": "success",
            "total_tokens": token_count,
            "intent": intent,
            "response_ms": elapsed_ms
        }
        yield f"event: done\ndata: {json.dumps(done_frame, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/v1/analysis/chat-stats")
async def get_chat_stats(range: str = "7d"):
    return {
        "total_sessions": 1280,
        "total_messages": 4860,
        "total_tokens_used": 1720000,
        "avg_response_ms": 680,
        "avg_tokens_per_answer": 354,
        "daily_trend": chat_stats_history,
        "intent_distribution": [
            {"intent": "配伍禁忌核验", "count": 1850},
            {"intent": "不良反应咨询", "count": 1240},
            {"intent": "指南方案推荐", "count": 980},
            {"intent": "用法用量核查", "count": 520},
            {"intent": "通用医学问诊", "count": 270}
        ],
        "top_asked_questions": [
            {"query": "卡托普利引起干咳能吃吗", "count": 320},
            {"query": "华法林和阿司匹林能一起吃吗", "count": 290},
            {"query": "左氧氟沙星和茶碱有冲突吗", "count": 240},
            {"query": "二甲双胍降糖用量注意", "count": 190},
            {"query": "布洛芬与降压药同服风险", "count": 160},
            {"query": "高血压合并糖尿病选什么药", "count": 140}
        ],
        "avg_hop_count_per_trace": 1.85,
        "cache_hit_rate": 0.38
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
