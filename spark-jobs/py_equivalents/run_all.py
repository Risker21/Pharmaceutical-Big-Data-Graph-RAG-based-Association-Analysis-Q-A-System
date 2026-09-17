# -*- coding: utf-8 -*-
import time
import importlib
from loguru import logger

jobs = [
    ("ODSToDWDPipeline", "01_ods_to_dwd"),
    ("Neo4jBulkLoader", "02_neo4j_bulk_loader"),
    ("MilvusIndexer", "03_milvus_indexer"),
    ("HBaseBulkLoader", "04_hbase_bulk_loader"),
    ("PageRankCalculator", "05_pagerank_calculator"),
    ("ADSPipeline", "06_ads_pipeline"),
    ("LouvainCommunity", "07_louvain_community")
]

def main():
    logger.info("=== Starting MedGraphRAG Full ETL & Graph Pipeline ===")
    total_start = time.time()
    for name, mod_name in jobs:
        t0 = time.time()
        mod = importlib.import_module(mod_name)
        res = mod.run()
        t1 = time.time()
        logger.info(f"==> Job [{name}] completed with {res.get('status')} in {t1-t0:.2f}s")
    logger.info(f"=== All 7 ETL Jobs finished in {time.time()-total_start:.2f}s ===")

if __name__ == "__main__":
    main()
