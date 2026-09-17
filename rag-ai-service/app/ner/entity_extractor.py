from typing import List, Tuple
import re

KNOWN_DRUGS = [
    "卡托普利", "依那普利", "二甲双胍", "格列美脲", "阿司匹林",
    "华法林", "左氧氟沙星", "茶碱", "奥美拉唑", "辛伐他汀",
    "硝苯地平", "美托洛尔", "氢氯噻嗪", "对乙酰氨基酚", "布洛芬",
    "螺内酯", "红霉素", "氨氯地平"
]

KNOWN_DISEASES = [
    "高血压", "2型糖尿病", "糖尿病", "冠心病", "心房颤动", "房颤",
    "慢性支气管炎", "支气管炎", "胃溃疡", "高脂血症", "偏头痛",
    "感冒", "骨关节炎", "关节炎"
]

KNOWN_SYMPTOMS = [
    "干咳", "水肿", "低血糖", "出血", "心律失常", "胃肠道反应", "肌肉痛", "头晕", "头痛", "发热"
]

def extract_entities(query: str) -> List[str]:
    found = []
    for d in KNOWN_DRUGS:
        if d in query and d not in found:
            found.append(d)
    for dis in KNOWN_DISEASES:
        if dis in query and dis not in found:
            found.append(dis)
    for sym in KNOWN_SYMPTOMS:
        if sym in query and sym not in found:
            found.append(sym)
    return found

def classify_intent(query: str, entities: List[str]) -> str:
    if any(w in query for w in ["同服", "一起吃", "相互作用", "合用", "禁忌", "冲突", "能吃吗"]):
        return "DRUG_INTERACTION"
    if any(w in query for w in ["副作用", "不良反应", "不舒服", "过敏"]):
        return "ADVERSE_REACTION"
    if any(w in query for w in ["治疗", "吃什么药", "用药", "指南", "方案"]):
        return "TREATMENT_PLAN"
    if any(w in query for w in ["用法", "用量", "剂量", "怎么吃"]):
        return "DOSAGE_USAGE"
    return "GENERAL_CONSULTATION"
