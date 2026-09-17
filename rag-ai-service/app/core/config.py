from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "MedGraphRAG-AIService"
    APP_ENV: str = "development"
    APP_PORT: int = 8000

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 2048
    USE_MOCK_LLM: bool = True

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j123"
    NEO4J_DATABASE: str = "neo4j"
    USE_MOCK_NEO4J: bool = True

    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "clinical_embeddings"
    VECTOR_DIM: int = 384
    USE_MOCK_MILVUS: bool = True

    HBASE_HOST: str = "localhost"
    HBASE_PORT: int = 9090
    HBASE_TABLE: str = "medical_corpus:drug_detail"
    USE_MOCK_HBASE: bool = True

    REDIS_URL: str = "redis://localhost:6379/2"
    USE_MOCK_REDIS: bool = True

    LOG_LEVEL: str = "INFO"
    ENABLE_CORS: bool = True
    CORS_ORIGINS: str = "*"

    HYBRID_TOP_K: int = 10
    RERANK_TOP_N: int = 6
    GRAPH_MAX_HOPS: int = 2

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [x.strip() for x in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
