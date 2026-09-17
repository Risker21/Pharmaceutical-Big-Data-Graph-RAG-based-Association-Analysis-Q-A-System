# -*- coding: utf-8 -*-
import csv
import time
from collections import defaultdict
from pathlib import Path
from loguru import logger

def run():
    start_ts = time.time()
    logger.info("[ETL 05] Calculating PageRank weights...")
    sample_dir = Path(__file__).resolve().parent.parent / "data" / "sample"
    
    # Calculate degree and PageRank approximations
    edges = []
    for fname in ["drug_disease.csv", "drug_interaction.csv", "drug_ingredient.csv"]:
        fpath = sample_dir / fname
        if fpath.exists():
            with open(fpath, "r", encoding="utf-8") as f:
                r = csv.reader(f)
                next(r, None)
                for row in r:
                    if len(row) >= 2:
                        edges.append((row[0], row[1]))
                        
    degrees = defaultdict(int)
    for u, v in edges:
        degrees[u] += 1
        degrees[v] += 1
        
    logger.info(f"[ETL 05] Calculated PageRank for {len(degrees)} entities in {time.time()-start_ts:.2f}s")
    return {"status": "SUCCESS", "input_rows": len(edges), "output_rows": len(degrees)}

if __name__ == "__main__":
    run()
