from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(title="MedGraphRAG Crawler Monitor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "UP", "timestamp": int(time.time()), "service": "data-crawler"}

@app.get("/metrics")
def get_metrics():
    return {
        "status": "HEALTHY",
        "active_crawlers": 3,
        "spiders": ["cmekg", "drug_label", "clinical_guideline"],
        "kafka_connected": True,
        "items_crawled_today": 1300,
        "kafka_topic_lag": 0
    }
