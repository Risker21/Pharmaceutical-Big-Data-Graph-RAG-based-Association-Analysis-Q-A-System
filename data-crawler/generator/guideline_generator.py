import hashlib
import json
import random
from pathlib import Path
from loguru import logger
from .rules import CORE_DISEASES, OUTPUT_DIR

random.seed(31)
SENTENCE_TEMPLATES = [
    "根据《{dept}诊疗指南（{yr}版）》，{disease}的一线治疗原则应优先选择{drug_cls}类药物。",
    "推荐等级：I类推荐；证据等级：A级。针对{disease}合并心血管高危因素的患者，建议初始联合{drug_cls}。",
    "用法用量：{drug_cls}起始剂量滴定，每 2~4 周评估靶目标，必要时加用联合方案。{special_tip}",
    "安全性管理：使用{drug_cls}期间需定期监测{monitor}，避免与 CYP450 强抑制剂联用。",
    "特殊人群：老年患者及 GFR<60 mL/min/1.73m² 的{disease}患者，{drug_cls}剂量需减半并密切观察。",
    "疗程与随访：{disease}治疗 {m} 个月后评估疗效，达标后维持长期治疗，每 {q} 月复查相关指标。",
    "专家共识要点：{disease}治疗核心靶点包括{target}，{drug_cls}在多项 RCT 中证明显著降低终点事件。",
    "药物相互作用警戒：{drug_cls}与 {interact_cls} 联用时存在 {risk_level} 级风险，参见相互作用模块详情。",
    "禁忌与慎用：对{drug_cls}过敏、{contra_situation}的{disease}患者应禁用，换用替代方案。",
    "患者教育：告知{disease}患者{drug_cls}最常见的不良反应为{adverse}，出现明显症状及时就医。",
]

SPECIAL_TIPS = {
    "ACEI": "需警惕首剂低血压及干咳，不耐受时换用 ARB。",
    "Biguanide": "造影前后 48h 暂停使用，预防乳酸酸中毒。",
    "Statin": "用药前及 3 个月后复查 ALT/AST，>3 倍 ULN 停药。",
    "Anticoagulant_VKA": "INR 稳定前每周监测，达标后每月 1 次，目标 2.0~3.0。",
    "default": "生活方式干预（低盐低脂饮食、规律运动、戒烟限酒）为基础。",
}
MONITORS = ["肝肾功能", "电解质+血钾", "INR+凝血功能", "血压+心率", "空腹血糖+HbA1c", "ALT/AST+CK"]
CONTRA_SITUATIONS = ["妊娠及哺乳期", "活动性出血", "严重肝肾功能不全", "已知药物过敏史", "急性冠脉综合征<24h"]
ADVERSES = ["轻度胃肠道反应", "头痛、头晕", "皮疹瘙痒", "肌肉酸痛乏力", "踝部水肿"]
TARGETS = ["RAAS 系统激活", "交感神经兴奋", "血小板聚集亢进", "血脂代谢紊乱", "胰岛素抵抗"]
INTERACT_PAIRS = [("ACEI", "螺内酯类利尿剂", "Medium"), ("华法林/VKA", "阿司匹林/NSAIDs", "High"),
                  ("喹诺酮类", "茶碱类", "High"), ("他汀", "CYP3A4 强抑制剂", "Medium")]
YR_POOL = [2018, 2019, 2020, 2021, 2022, 2023, 2024]


def run_generate_guidelines():
    guideline_jsonl = OUTPUT_DIR / "clinical_guideline.jsonl"
    sample_dir = Path(__file__).resolve().parent.parent.parent / "spark-jobs" / "data" / "sample"
    sample_dir.mkdir(parents=True, exist_ok=True)
    guideline_json = sample_dir / "clinical_guidelines.json"

    drug_classes_order = ["ACEI", "Biguanide", "Sulfonylurea", "Antiplatelet", "Anticoagulant_VKA",
                          "Quinolone", "Methylxanthine", "PPI", "Statin", "CCB", "BetaBlocker",
                          "ThiazideDiuretic", "Antipyretic_Analgesic", "NSAID"]
    disease_pool = CORE_DISEASES * 5
    out_objs = []
    chunk_id = 1
    for disease, icd, dept, *_ in disease_pool:
        for cls in drug_classes_order:
            for _tmpl_idx, template in enumerate(SENTENCE_TEMPLATES):
                yr = random.choice(YR_POOL)
                tip = SPECIAL_TIPS.get(cls, SPECIAL_TIPS["default"])
                m = random.choice([1, 2, 3, 6, 12])
                q = random.choice([1, 2, 3, 6])
                monitor = random.choice(MONITORS)
                contra = random.choice(CONTRA_SITUATIONS)
                adverse = random.choice(ADVERSES)
                target = random.choice(TARGETS)
                interact_pair = random.choice(INTERACT_PAIRS)
                interact_cls, interact_lvl = interact_pair[1], interact_pair[2]
                text = template.format(
                    disease=disease, dept=dept, yr=yr, drug_cls=cls,
                    special_tip=tip, monitor=monitor, m=m, q=q,
                    contra_situation=contra, adverse=adverse, target=target,
                    interact_cls=interact_cls, risk_level=interact_lvl,
                )
                obj = {
                    "chunk_id": chunk_id,
                    "content": text,
                    "source": f"中华医学会{dept}学分会 {yr} 专家共识",
                    "publish_year": yr,
                    "drug_refs": [cls],
                    "disease_refs": [disease, icd],
                }
                out_objs.append(obj)
                chunk_id += 1
                if chunk_id > 1050:
                    break
            if chunk_id > 1050:
                break
        if chunk_id > 1050:
            break

    with open(guideline_jsonl, "w", encoding="utf-8") as f:
        for o in out_objs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    with open(guideline_json, "w", encoding="utf-8") as f:
        json.dump(out_objs, f, ensure_ascii=False, indent=2)
    logger.info(f"[GuidelineGen] {len(out_objs)} chunks → {guideline_json}, {guideline_jsonl}")
    return out_objs
