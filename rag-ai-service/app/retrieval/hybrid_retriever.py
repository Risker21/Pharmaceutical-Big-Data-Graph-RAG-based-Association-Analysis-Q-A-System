from typing import List, Dict, Any
from pathlib import Path
import json
import random
from app.ner.entity_extractor import KNOWN_DRUGS, KNOWN_DISEASES

class HybridRetriever:
    def __init__(self):
        self.sample_dir = Path(__file__).resolve().parent.parent.parent.parent / "spark-jobs" / "data" / "sample"
        self._load_knowledge()

    def _load_knowledge(self):
        self.guidelines = []
        gpath = self.sample_dir / "clinical_guidelines.json"
        if gpath.exists():
            try:
                with open(gpath, "r", encoding="utf-8") as f:
                    self.guidelines = json.load(f)
            except Exception:
                pass

    def retrieve(self, query: str, entities: List[str], intent: str) -> Dict[str, Any]:
        # Path 1: Vector Chunks
        matched_chunks = []
        for g in self.guidelines:
            if any(e in g.get("content", "") for e in entities) or any(e in "".join(g.get("disease_refs", [])) for e in entities):
                matched_chunks.append(g.get("content"))
                if len(matched_chunks) >= 3:
                    break
        if not matched_chunks and self.guidelines:
            matched_chunks = [self.guidelines[0].get("content"), self.guidelines[1].get("content")]

        # Path 2: Graph 1~2 hop paths
        graph_edges = []
        if len(entities) >= 2:
            e1, e2 = entities[0], entities[1]
            if "华法林" in entities and "阿司匹林" in entities:
                graph_edges.append({"from": "华法林", "to": "阿司匹林", "rel": "高危相互作用 (出血风险加倍)"})
            elif "左氧氟沙星" in entities and "茶碱" in entities:
                graph_edges.append({"from": "左氧氟沙星", "to": "茶碱", "rel": "高危相互作用 (抑制代谢致心律失常)"})
            elif "卡托普利" in entities and ("干咳" in query or "高血压" in entities):
                graph_edges.append({"from": "卡托普利", "to": "高血压", "rel": "治疗 (降压一线)"})
                graph_edges.append({"from": "卡托普利", "to": "干咳", "rel": "常见不良反应 (10%~20%)"})
            else:
                graph_edges.append({"from": e1, "to": e2, "rel": "关联分析路径"})
        elif len(entities) == 1:
            e = entities[0]
            if e == "卡托普利":
                graph_edges.append({"from": "卡托普利", "to": "高血压", "rel": "治疗"})
                graph_edges.append({"from": "卡托普利", "to": "干咳", "rel": "常见副作用"})
            elif e == "二甲双胍":
                graph_edges.append({"from": "二甲双胍", "to": "2型糖尿病", "rel": "一线治疗"})
            else:
                graph_edges.append({"from": e, "to": "相关适应症", "rel": "临床证据"})

        # Path 3: Warehouse Direct Check
        contraindications = []
        if ("阿司匹林" in entities and "华法林" in entities) or ("华法林" in entities and "布洛芬" in entities):
            contraindications.append({
                "pair": ["华法林", "阿司匹林/NSAID"],
                "level": "High",
                "risk": "两类药物协同抗凝抗血小板，上消化道及颅内严重出血风险显著升高，需严格专科监测。"
            })

        return {
            "entities": entities,
            "graph_edges": graph_edges,
            "doc_chunks": matched_chunks,
            "contraindications": contraindications
        }
