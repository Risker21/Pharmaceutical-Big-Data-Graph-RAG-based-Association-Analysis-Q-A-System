from functools import lru_cache

from app.core.llm_client import LLMClient, MockLLM, OpenAICompatibleLLM, get_llm_client
from app.ner.medical_dict import MedicalDictionary
from app.ner.entity_extractor import EntityExtractor
from app.ner.intent_classifier import IntentClassifier, MedicalIntent
from app.retrieval.vector_retriever import VectorRetriever
from app.retrieval.graph_retriever import GraphRetriever
from app.retrieval.warehouse_retriever import WarehouseRetriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.rerank.cross_encoder_reranker import CrossEncoderReranker
from app.prompt.assembler import PromptAssembler
from app.generators.answer_generator import AnswerGenerator
from app.generators.trace_formatter import TraceFormatter


class NERPipeline:
    def __init__(self):
        self.dictionary = MedicalDictionary()
        self.extractor = EntityExtractor(self.dictionary)
        self.classifier = IntentClassifier()

    def extract_entities_and_intent(self, query: str):
        entities = self.extractor.extract(query)
        intent = self.classifier.classify(query, entities)
        return entities, intent


_ner_pipeline = None
_hybrid_retriever = None
_answer_generator = None
_trace_formatter = None
_prompt_assembler = None
_reranker = None


def get_ner_pipeline() -> NERPipeline:
    global _ner_pipeline
    if _ner_pipeline is None:
        _ner_pipeline = NERPipeline()
    return _ner_pipeline


def get_reranker() -> CrossEncoderReranker:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoderReranker()
    return _reranker


def get_prompt_assembler() -> PromptAssembler:
    global _prompt_assembler
    if _prompt_assembler is None:
        _prompt_assembler = PromptAssembler()
    return _prompt_assembler


def get_trace_formatter() -> TraceFormatter:
    global _trace_formatter
    if _trace_formatter is None:
        _trace_formatter = TraceFormatter()
    return _trace_formatter


def get_hybrid_retriever() -> HybridRetriever:
    global _hybrid_retriever
    if _hybrid_retriever is None:
        vr = VectorRetriever()
        gr = GraphRetriever()
        wr = WarehouseRetriever()
        rr = get_reranker()
        _hybrid_retriever = HybridRetriever(vr, gr, wr, rr)
    return _hybrid_retriever


def get_answer_generator() -> AnswerGenerator:
    global _answer_generator
    if _answer_generator is None:
        llm = get_llm_client()
        pa = get_prompt_assembler()
        tf = get_trace_formatter()
        _answer_generator = AnswerGenerator(llm, pa, tf)
    return _answer_generator
