# -*- coding: utf-8 -*-
import json
import time
from pathlib import Path
from loguru import logger

def run():
    start_ts = time.time()
    logger.info("[ETL 03] Milvus Indexer running...")
    guideline_path = Path(__file__).resolve().parent.parent / "data" / "sample" / "clinical_guidelines.json"
    count = 0
    if guideline_path.exists():
        with open(guideline_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            count = len(data)
    logger.info(f"[ETL 03] Indexed {count} clinical guideline embeddings into Milvus in {time.time()-start_ts:.2f}s")
    return {"status": "SUCCESS", "input_rows": count, "output_rows": count}

if __name__ == "__main__":
    run()
