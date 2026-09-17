import os
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
COLLECTION_NAME = os.getenv("MILVUS_COLLECTION", "clinical_embeddings")
DIM = int(os.getenv("MILVUS_VECTOR_DIM", "384"))
print(f"[Milvus Init] Configuration: host={MILVUS_HOST}:{MILVUS_PORT}, collection={COLLECTION_NAME}, dim={DIM}")
