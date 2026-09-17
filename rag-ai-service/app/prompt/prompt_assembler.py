from typing import Dict, Any

PROMPT_TEMPLATE = """你是一名专业、严谨的临床医药知识图谱问答助手（MedGraphRAG Assistant）。
请根据以下检索到的【知识图谱拓扑事实】、【数仓配伍禁忌矩阵】及【权威临床指南切片】，针对用户的医学咨询提供结构化、具备推导链条且可溯源的解答。

【用户提问】：{query}
【医学实体识别】：{entities}
【知识图谱推导路径】：
{graph_paths}
【数仓配伍禁忌核验】：
{contraindications}
【参考临床指南文献】：
{guidelines}

【回答要求】：
1. 优先遵循知识图谱实体关系与数仓禁忌事实，若存在高危禁忌必须在首段醒目提示风险。
2. 解释药理机制并推导用药逻辑，引用具体指南或说明书依据。
3. 给出明确的临床监测建议（如监测血压、血钾、血糖或凝血指标）或替代方案。
4. 语言专业、客观，文末附带就医遵医嘱提醒。
"""

class PromptAssembler:
    def assemble(self, query: str, context: Dict[str, Any]) -> str:
        entities_str = "、".join(context.get("entities", [])) or "通用咨询"
        
        edges = context.get("graph_edges", [])
        graph_str = "\n".join([f"- ({e.get('from')}) --[{e.get('rel')}]--> ({e.get('to')})" for e in edges]) if edges else "无特定跳步路径"
        
        contras = context.get("contraindications", [])
        contra_str = "\n".join([f"- [风险等级: {c.get('level')}] {c.get('risk')}" for c in contras]) if contras else "未检索到硬性配伍禁忌阻断规则"
        
        chunks = context.get("doc_chunks", [])
        chunks_str = "\n".join([f"[{i+1}] {c}" for i, c in enumerate(chunks)]) if chunks else "无特定指南文献"
        
        return PROMPT_TEMPLATE.format(
            query=query,
            entities=entities_str,
            graph_paths=graph_str,
            contraindications=contra_str,
            guidelines=chunks_str
        )
