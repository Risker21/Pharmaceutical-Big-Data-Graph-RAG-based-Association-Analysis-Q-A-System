import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.ner.entity_extractor import extract_entities, classify_intent
from app.retrieval.hybrid_retriever import HybridRetriever
from app.prompt.prompt_assembler import PromptAssembler

def test_captopril_adverse_retrieval():
    query = "高血压患者合并干咳，可以用卡托普利吗？"
    entities = extract_entities(query)
    intent = classify_intent(query, entities)
    assert "卡托普利" in entities
    assert "高血压" in entities
    
    retriever = HybridRetriever()
    context = retriever.retrieve(query, entities, intent)
    assert len(context["graph_edges"]) > 0
    
    prompt = PromptAssembler().assemble(query, context)
    assert "卡托普利" in prompt

def test_warfarin_aspirin_contraindication():
    query = "华法林和阿司匹林能一起吃吗？"
    entities = extract_entities(query)
    assert "华法林" in entities
    assert "阿司匹林" in entities
    
    retriever = HybridRetriever()
    context = retriever.retrieve(query, entities, "DRUG_INTERACTION")
    assert len(context["contraindications"]) > 0
    assert context["contraindications"][0]["level"] == "High"

if __name__ == "__main__":
    test_captopril_adverse_retrieval()
    test_warfarin_aspirin_contraindication()
    print("[OK] RAG Hybrid Retrieval Tests Passed!")
