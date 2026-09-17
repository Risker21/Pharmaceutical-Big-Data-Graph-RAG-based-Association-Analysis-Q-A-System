import csv
import json
import random
import hashlib
from pathlib import Path
from loguru import logger
from .rules import CORE_DRUGS, DOSAGE_FORMS, OUTPUT_DIR

random.seed(42)
SYNTH_SIZE = 200

PREFIXES = ["盐酸", "马来酸", "酒石酸", "左旋", "苯磺酸", "琥珀酸", "瑞舒", "阿托", "缬沙", "替米"]
SUFFIXES = list(DOSAGE_FORMS)


def generate_drug_id(name: str) -> str:
    return "DR" + hashlib.md5(name.encode("utf-8")).hexdigest()[:10].upper()


def _export_association_csvs(results, base_path: Path):
    from .rules import CORE_DISEASES, CORE_INGREDIENTS
    drug_ingredient_csv = base_path / "drug_ingredient.csv"
    drug_disease_csv = base_path / "drug_disease.csv"
    disease_symptom_csv = base_path / "disease_symptom.csv"
    ingredients_csv = base_path / "ingredients.csv"

    with open(ingredients_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ingredient_id", "name", "molecular_weight"])
        for ing_id, name, mw in CORE_INGREDIENTS:
            w.writerow([ing_id, name, mw])

    drug_name_to_id = {d["name"]: generate_drug_id(d["name"]) for d in results}
    ing_name_to_id = {name: iid for iid, name, _ in CORE_INGREDIENTS}

    with open(drug_ingredient_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["drug_id", "ingredient_id", "dose"])
        for d in results:
            did = drug_name_to_id[d["name"]]
            for ing_name, dose in d["ingredients"]:
                iid = ing_name_to_id.get(ing_name, f"ING_EXT_{ing_name}")
                w.writerow([did, iid, dose])

    with open(drug_disease_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["drug_id", "disease_id", "efficacy"])
        for d in results:
            did = drug_name_to_id[d["name"]]
            drug_cls = d["class"]
            for dis_name, icd, dept, symps, treats in CORE_DISEASES:
                dis_id = "DI" + hashlib.md5(dis_name.encode("utf-8")).hexdigest()[:10].upper()
                if any(tc[:4] in drug_cls or tc[:3] in drug_cls or drug_cls[:3] in tc for tc in treats):
                    eff = round(random.uniform(0.45, 0.92), 2)
                    w.writerow([did, dis_id, eff])

    with open(disease_symptom_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["disease_id", "symptom_id", "probability"])
        symptom_name_to_id = {}
        for i, sname in enumerate(CORE_DISEASES[0][3] + CORE_DISEASES[2][3], start=1):
            if sname not in symptom_name_to_id:
                symptom_name_to_id[sname] = f"SY{i:03d}"
        for dis_name, icd, dept, symps, treats in CORE_DISEASES:
            dis_id = "DI" + hashlib.md5(dis_name.encode("utf-8")).hexdigest()[:10].upper()
            for s in symps:
                sid = symptom_name_to_id.get(s, f"SY_EXT_{s}")
                prob = round(random.uniform(0.35, 0.95), 2)
                w.writerow([dis_id, sid, prob])


def run_generate_drugs():
    drugs_out_jsonl = OUTPUT_DIR / "drug_label.jsonl"
    sample_dir = Path(__file__).resolve().parent.parent.parent / "spark-jobs" / "data" / "sample"
    drugs_out_csv = sample_dir / "drugs.csv"
    sample_dir.mkdir(parents=True, exist_ok=True)

    results = list(CORE_DRUGS)
    for idx in range(SYNTH_SIZE - len(CORE_DRUGS)):
        tpl = random.choice(CORE_DRUGS)
        clean_name = tpl["name"].replace("盐酸", "").replace("马来酸", "").replace("酒石酸", "")
        new_name = random.choice(PREFIXES) + clean_name + random.choice(SUFFIXES)
        if any(r["name"] == new_name for r in results):
            continue
        results.append({
            "name": new_name,
            "class": tpl["class"],
            "indication": tpl["indication"],
            "contra": tpl["contra"],
            "adverse": tpl["adverse"],
            "ingredients": [(ing[0], f"{random.randint(5,500)}mg/片") for ing in tpl["ingredients"]],
            "approval_no": f"国药准字H{20000000+idx}",
        })

    with open(drugs_out_jsonl, "w", encoding="utf-8") as f:
        for d in results:
            item = {
                "drug_id": generate_drug_id(d["name"]),
                "name": d["name"],
                "approval_no": d["approval_no"],
                "dosage_form": d["ingredients"][0][1].split("/")[-1],
                "spec": d["ingredients"][0][1],
                "usage": f"口服，每日 1~2 次，按{random.choice(['餐前','餐后','餐中'])}服用，或遵医嘱调整剂量。",
                "adverse_reaction": "；".join(d["adverse"]),
                "contraindication_text": "；".join(d["contra"]),
                "pharmacology_text": f"药理分类为{d['class']}。适应症包括：{'、'.join(d['indication'])}。",
                "ingredients": [x[0] for x in d["ingredients"]],
            }
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(drugs_out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["drug_id", "name", "approval_no", "dosage_form", "spec", "usage", "adverse_reaction",
                    "contraindication_text", "pharmacology_text"])
        for d in results:
            di = generate_drug_id(d["name"])
            w.writerow([
                di, d["name"], d["approval_no"], d["ingredients"][0][1].split("/")[-1],
                d["ingredients"][0][1],
                "口服，每日1~2次。",
                "；".join(d["adverse"]),
                "；".join(d["contra"]),
                f"药理分类：{d['class']}  适应症：{'、'.join(d['indication'])}。",
            ])

    _export_association_csvs(results, sample_dir)
    logger.info(f"[DrugGen] {len(results)} drugs → {drugs_out_jsonl}, {drugs_out_csv}")
    return results
