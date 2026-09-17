import csv
import json
import random
from pathlib import Path
from loguru import logger
from .rules import INTERACTION_RULES, CYP3A4_INHIBITORS, SPIRO_LIKE, OUTPUT_DIR


_seed_done = False


def ensure_generator_seed():
    global _seed_done
    if _seed_done:
        return
    _seed_done = True
    random.seed(42)


def _class_of(drug_meta, name):
    if name in CYP3A4_INHIBITORS:
        drug_meta.setdefault(name, set()).add("CYP3A4_Inhibitor")
    if name in SPIRO_LIKE:
        drug_meta.setdefault(name, set()).add("Spironolactone_like")
    return drug_meta.get(name, set())


def run_generate_interactions(drug_core=None, output_pair_file=None):
    ensure_generator_seed()
    from .rules import CORE_DRUGS
    from .drug_generator import generate_drug_id
    drug_core = drug_core or [(d["name"], d["class"]) for d in CORE_DRUGS]
    drugs_meta = {n: {cls} for n, cls in drug_core}
    for n in list(drugs_meta.keys()):
        _class_of(drugs_meta, n)
    cls_to_drugs = {}
    for n, classes in drugs_meta.items():
        for c in classes:
            cls_to_drugs.setdefault(c, []).append(n)

    pairs = {}
    for rule in INTERACTION_RULES:
        (ca, cb), lvl, risk, base_cnt = rule["classes"], rule["level"], rule["risk_detail"], rule["case_count_base"]
        same_only = rule.get("same_class_only", False)
        la = [d for c in ca for d in cls_to_drugs.get(c, [])]
        lb = [d for c in cb for d in cls_to_drugs.get(c, [])]
        for a in la:
            for b in lb:
                if a == b:
                    if not same_only:
                        continue
                key = tuple(sorted((a, b)))
                if key in pairs:
                    continue
                case_cnt = base_cnt + random.randint(-50, 200)
                pairs[key] = (lvl, risk, case_cnt)

    all_names = list(drugs_meta.keys())
    while len(pairs) < 520:
        a, b = random.sample(all_names, k=2)
        key = tuple(sorted((a, b)))
        if key in pairs:
            continue
        lvl = random.choices(["Low", "Medium"], weights=[0.7, 0.3])[0]
        detail = ("目前无强临床证据的严重相互作用，建议监测生命体征及症状。"
                  if lvl == "Low" else "可能存在轻度药代动力干扰，老年/肝肾功能不全者需密切观察。")
        pairs[key] = (lvl, detail, random.randint(50, 300))

    out_jsonl = OUTPUT_DIR / "interactions.jsonl"
    sample_dir = Path(__file__).resolve().parent.parent.parent / "spark-jobs" / "data" / "sample"
    pair_csv = sample_dir / "drug_interaction.csv"
    sample_dir.mkdir(parents=True, exist_ok=True)
    with open(out_jsonl, "w", encoding="utf-8") as fj, \
         open(pair_csv, "w", encoding="utf-8", newline="") as fc:
        w = csv.writer(fc)
        w.writerow(["drug_a_id", "drug_b_id", "level", "risk_detail", "case_count"])
        for (a, b), (lvl, detail, cnt) in pairs.items():
            ai, bi = generate_drug_id(a), generate_drug_id(b)
            fj.write(json.dumps({
                "drug_a": a, "drug_a_id": ai, "drug_b": b, "drug_b_id": bi,
                "level": lvl, "risk_detail": detail, "case_count": cnt,
            }, ensure_ascii=False) + "\n")
            w.writerow([ai, bi, lvl, detail, cnt])
            w.writerow([bi, ai, lvl, detail, cnt])
    high_count = sum(1 for v in pairs.values() if v[0] == "High")
    logger.info(f"[InteractGen] {len(pairs)} pairs generated ({high_count} High-level)")
    return pairs
