import asyncio
from typing import AsyncGenerator, Dict, Any

KNOWLEDGE_ANSWERS = {
    ("卡托普利", "干咳"): """根据医药知识图谱与临床用药指南分析如下：

1. **药理机制与不良反应溯源**：
   卡托普利属于血管紧张素转换酶抑制剂（ACEI）。该类药物在阻断血管紧张素II生成的同时，会抑制缓激肽的水解降解，导致气道内缓激肽及P物质局部积蓄，从而刺激气道咳嗽反射受体，引发特征性的**无痰顽固性干咳**（临床发生率约为10%~20%）。

2. **用药建议与替代方案**：
   - 如果患者干咳症状明显影响睡眠与日常生活，**不建议继续强行使用卡托普利**。
   - 建议在专科医师指导下转换为**血管紧张素II受体拮抗剂（ARB类）**，例如氯沙坦、缬沙坦或替米沙坦。ARB类药物直接阻断AT1受体而不影响缓激肽代谢，极少诱发干咳。
   - 亦可考虑联合钙通道阻滞剂（CCB，如氨氯地平）进行血压达标管理。

3. **临床监测提醒**：
   换药期间请持续监测坐位血压及血钾水平，遵医嘱进行剂量滴定。""",

    ("阿司匹林", "华法林"): """【高风险配伍禁忌警戒】根据知识图谱相互作用矩阵核验，阿司匹林与华法林联用属于 **High 级高危风险组合**：

1. **协同致出血机制**：
   - **华法林**为维生素K拮抗剂，阻断凝血因子II、VII、IX、X的合成；
   - **阿司匹林**通过不可逆抑制环氧合酶-1（COX-1）抑制血小板聚集，同时直接对胃胃黏膜具有侵蚀损伤作用。
   - 两者联合使用使上消化道出血及严重颅内出血发生风险提升 2~3 倍（RR≈3.2）。

2. **临床处置原则**：
   - 除急性冠脉综合征（ACS）合并机械瓣置换术后等严格专科指征外，**不推荐常规联合口服**。
   - 若确需联合抗栓治疗，须在心内科医师指导下严密监测 **INR 指标（建议严格控制在 2.0~2.5）**，并常规联合质子泵抑制剂（PPI，如奥美拉唑）进行胃黏膜保护。""",

    ("左氧氟沙星", "茶碱"): """【高风险配伍禁忌警戒】左氧氟沙星与茶碱合用属于 **High 级高危药物相互作用**：

1. **代谢抑制与蓄积毒性**：
   左氧氟沙星可显著抑制肝微粒体细胞色素P450酶系统中的 **CYP1A2 同工酶**，导致茶碱在体内的清除率下降约30%~50%，茶碱血药浓度异常升高达 2~4 倍。

2. **潜在不良后果**：
   茶碱治疗窗较窄，血药浓度过高极易诱发严重的**恶心剧烈呕吐、室性心律失常甚至中枢惊厥惊厥发作**。

3. **应对措施**：
   - 如必须联用，茶碱剂量建议减半，并密切监测茶碱血药谷浓度（安全目标 5~15 μg/mL）；
   - 或改用对 CYP1A2 无显著抑制作用的抗菌药物（如头孢类或阿奇霉素）。"""
}

DEFAULT_ANSWER_TEMPLATE = """根据医药知识图谱与临床指南检索结果：

针对您咨询的【{query}】：
1. **疾病与药物关联**：已在图谱中定位到相关医学实体（{entities}），相关药物通过特定生物靶点调节病理生理过程。
2. **用药指导与注意事项**：
   - 请按说明书推荐剂量或专科医嘱规范服用，避免自行增减剂量或擅自停药；
   - 关注可能伴随的轻微胃肠道反应或血压/血糖波动，定期随访复查肝肾功能与生命体征。
3. **安全提示**：若出现持续不适或过敏反应，请立即前往医院专科就诊。"""

class MockLLMGenerator:
    async def stream_generate(self, query: str, context: Dict[str, Any]) -> AsyncGenerator[str, None]:
        entities = context.get("entities", [])
        
        # Match specific high-yield question templates
        matched_text = None
        for key_pair, answer in KNOWLEDGE_ANSWERS.items():
            if all(k in query or k in entities for k in key_pair):
                matched_text = answer
                break
                
        if not matched_text:
            ent_str = "、".join(entities) if entities else "相关疾病/药品"
            matched_text = DEFAULT_ANSWER_TEMPLATE.format(query=query, entities=ent_str)

        # Stream out tokens
        chunk_size = 4
        for i in range(0, len(matched_text), chunk_size):
            chunk = matched_text[i:i+chunk_size]
            yield chunk
            await asyncio.sleep(0.02)
