import csv
import hashlib
import json
import random
from pathlib import Path
from loguru import logger
from .rules import CORE_DISEASES, OUTPUT_DIR, CORE_SYMPTOMS

random.seed(7)
SYNTH_SIZE = 50


def generate_disease_id(name: str) -> str:
    return "DI" + hashlib.md5(name.encode("utf-8")).hexdigest()[:10].upper()


def run_generate_diseases():
    diseases_out_jsonl = OUTPUT_DIR / "cmekg.jsonl"
    sample_dir = Path(__file__).resolve().parent.parent.parent / "spark-jobs" / "data" / "sample"
    diseases_csv = sample_dir / "diseases.csv"
    symptoms_csv = sample_dir / "symptoms.csv"
    sample_dir.mkdir(parents=True, exist_ok=True)

    results = list(CORE_DISEASES)
    extra = []
    for name, icd, dept, symp, treat in CORE_DISEASES:
        for i in range(4):
            new = f"{name}（{random.choice(['合并高脂血症','老年型','不典型型','重度','轻度','急性期','稳定期'])}）"
            icd_new = f"{icd}.{i+1}"
            extra.append((new, icd_new, dept, random.sample(symp, k=min(3, len(symp))), treat))
    results.extend(extra[:SYNTH_SIZE - len(results)])

    with open(diseases_out_jsonl, "w", encoding="utf-8") as f:
        for n, icd, dep, symps, treats in results:
            f.write(json.dumps({
                "disease_id": generate_disease_id(n),
                "name": n, "icd_code": icd, "aliases": [n], "department": dep,
                "symptoms": list(symps), "treatments": treats,
            }, ensure_ascii=False) + "\n")

    with open(diseases_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["disease_id", "name", "icd_code", "department", "description"])
        for n, icd, dep, symps, _ in results:
            w.writerow([generate_disease_id(n), n, icd, dep, f"典型症状：{'、'.join(symps)}。"])

    with open(symptoms_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["symptom_id", "name", "description"])
        for i, (n, desc) in enumerate(CORE_SYMPTOMS, start=1):
            w.writerow([f"SY{i:03d}", n, desc])
    logger.info(f"[DiseaseGen] {len(results)} diseases + {len(CORE_SYMPTOMS)} symptoms")
    return results
