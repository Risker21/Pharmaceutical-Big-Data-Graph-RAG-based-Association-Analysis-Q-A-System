# -*- coding: utf-8 -*-
import csv
import json
import time
from pathlib import Path
from loguru import logger

def run():
    start_ts = time.time()
    logger.info("[ETL 01] Starting ODS -> DWD transformation...")
    base_dir = Path(__file__).resolve().parent.parent
    sample_dir = base_dir / "data" / "sample"
    ods_dir = base_dir.parent / "data-crawler" / "output" / "ods_raw"
    
    # Process drug dimension
    drug_rows = []
    drug_source = ods_dir / "drug_label.jsonl"
    if drug_source.exists():
        with open(drug_source, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    drug_rows.append([
                        item.get("drug_id"), item.get("name"), item.get("approval_no"),
                        item.get("dosage_form"), item.get("spec"), item.get("usage"),
                        item.get("adverse_reaction"), item.get("contraindication_text"),
                        item.get("pharmacology_text")
                    ])
    
    logger.info(f"[ETL 01] Processed {len(drug_rows)} drug dimension records in {time.time()-start_ts:.2f}s")
    return {"status": "SUCCESS", "input_rows": len(drug_rows), "output_rows": len(drug_rows)}

if __name__ == "__main__":
    run()
