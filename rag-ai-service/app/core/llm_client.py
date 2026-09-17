import time
import re
from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Optional
from dataclasses import dataclass

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ChatMessage:
    role: str
    content: str


class LLMClient(ABC):
    @abstractmethod
    async def chat_completion(
        self, messages: List[ChatMessage], stream: bool = False
    ) -> AsyncGenerator[str, None]:
        pass


MOCK_QA_PAIRS = [
    {
        "keywords": ["华法林", "阿司匹林", "同服", "合用", "一起", "联用"],
        "answer": (
            "【核心结论】华法林（抗凝药，VKA类）与阿司匹林（抗血小板药，COX抑制剂）常规不建议同服，"
            "两者联用会使出血事件（消化道出血、颅内出血）发生率升高2~3倍，风险显著增加。\n\n"
            "【循证依据】\n"
            "1. 药理机制叠加：华法林抑制维生素K依赖凝血因子(II/VII/IX/X)合成，阿司匹林不可逆抑制血小板COX-1减少TXA2生成，"
            "两条凝血通路同时阻断，止血能力严重下降。\n"
            "2. 临床证据：RE-LY、ARISTOTLE等大型RCT的亚组分析显示，VKA+单药抗血小板使主要出血RR≈1.7，"
            "VKA+DAPT（阿司匹林+氯吡格雷）使出血RR≈2.3~3.1。\n\n"
            "【特殊情况】ACS合并机械瓣/CHA2DS2-VASc≥3等高凝状态患者，经心血管专科严格评估后可短期三联或二联抗栓，"
            "但必须：①严格控制INR 2.0~3.0（目标2.5）；②联用PPI（如奥美拉唑20mg qd）预防消化道出血；"
            "③缩短INR监测间隔（每周1~2次）；④尽量缩短联用疗程。\n\n"
            "【用药建议】如仅为房颤抗凝或DVT二级预防，应单独使用华法林（或换用NOAC），不要常规加用阿司匹林；"
            "如已联用，建议MDT会诊重新评估抗栓方案。"
        ),
    },
    {
        "keywords": ["卡托普利", "干咳", "副作用", "不良反应"],
        "answer": (
            "【核心结论】干咳是卡托普利（ACEI类）最典型的不良反应，发生率约10%~20%，"
            "多为刺激性无痰咳，夜间或卧位加重，通常在用药1周至数月内出现，停药后1~2周可缓解。\n\n"
            "【发生机制】ACEI同时抑制ACE降解缓激肽（BK），使BK在气道黏膜蓄积，刺激C纤维感受器，引起反射性咳嗽；"
            "此外BK诱导的前列腺素释放、气道上皮损伤也参与其中。东亚人群（尤其中国人）发生率显著高于欧美人群。\n\n"
            "【处理建议】\n"
            "1. 轻度干咳：可先观察，部分患者2~4周后耐受减轻；同时建议睡前3小时服药、多饮水、避免烟雾刺激。\n"
            "2. 中度干咳影响生活：加用色甘酸钠气雾剂，或临时服用孟鲁司特10mg qn缓解症状。\n"
            "3. 重度不耐受：换用ARB类（如缬沙坦80mg qd、厄贝沙坦150mg qd），ARBs不抑制BK降解，干咳发生率<3%，"
            "降压强度与靶器官保护作用与ACEI相当。\n\n"
            "【鉴别】需先排除其他致咳原因：慢性支气管炎、左心衰肺水肿、胃食管反流、间质性肺病、ACEI诱发的血管性水肿（罕见但致命）。"
        ),
    },
    {
        "keywords": ["左氧氟沙星", "左氧", "茶碱", "相互作用", "合用", "联用"],
        "answer": (
            "【核心结论】左氧氟沙星（氟喹诺酮类）与茶碱（黄嘌呤类）存在【高风险】药物相互作用，禁止常规联用；"
            "联用可使茶碱血药浓度升高2~4倍，诱发严重心律失常、惊厥甚至死亡。\n\n"
            "【相互作用机制】左氧氟沙星可逆性抑制肝细胞色素P450 CYP1A2酶活性，而茶碱约70%经CYP1A2代谢清除，"
            "两者竞争代谢位点导致茶碱清除率下降30%~50%，半衰期延长，血药谷浓度远超安全窗（10~20mg/L）。\n\n"
            "【危险信号】联用后出现心悸、恶心呕吐、烦躁失眠、震颤、多源性室早、QT间期延长者需立即停药急诊，"
            "监测茶碱血药浓度及心电图，必要时血液灌流清除。\n\n"
            "【替代方案】\n"
            "1. 抗感染换用：呼吸道感染可选阿莫西林克拉维酸钾、头孢呋辛酯、阿奇霉素（大环内酯类对CYP1A2抑制较弱）；\n"
            "2. 平喘换用：慢阻肺/哮喘可用多索茶碱（代谢不依赖CYP1A2，相互作用风险低，负荷量200mg ivgtt bid）"
            " 或吸入LABA/ICS复方制剂（如沙美特罗替卡松），不经过CYP450首过代谢。\n\n"
            "【极端特殊情况】若必须联用（无其他可选药），茶碱剂量必须减量50%，每24小时监测茶碱谷浓度，维持5~10mg/L低限，"
            "持续心电监护，住院观察下使用。"
        ),
    },
    {
        "keywords": ["二甲双胍", "糖尿病", "降糖", "2型糖尿病"],
        "answer": (
            "【核心结论】二甲双胍（双胍类）是2型糖尿病（T2DM）一线首选用药，贯穿糖尿病治疗全程，"
            "若无禁忌证（eGFR<30ml/min、乳酸酸中毒史、造影前后48h）应持续保留在治疗方案中。\n\n"
            "【药理优势】\n"
            "1. 靶点明确：激活AMPK通路，减少肝脏糖异生，增加外周组织（肌肉/脂肪）胰岛素敏感性，轻度延迟肠道葡萄糖吸收；\n"
            "2. 降糖确切：HbA1c降幅1.0%~1.5%，不增加体重，不诱发低血糖（单药）；\n"
            "3. 心血管获益：UKPDS 10年随访证实二甲双胍可降低T2DM合并超重患者的全因死亡率（RR=0.64）和心梗风险（RR=0.61）；\n"
            "4. 性价比极高：全球医保覆盖，日治疗费用<2元。\n\n"
            "【用法用量】起始500mg tid 餐中/餐后服，每周递增500mg，目标日剂量1500~2000mg（分2~3次），最大日剂量不超过2550mg。"
            " 缓释片可1500mg qd 晚餐后服，减少胃肠道反应。\n\n"
            "【常见不良反应处理】\n"
            "• 恶心、腹泻、腹胀（20%~30%）：餐中服药、从小剂量起始缓慢滴定，1~2周多自行缓解；\n"
            "• 维生素B12缺乏（长期用）：每年检测血清B12，必要时补充甲钴胺500μg tid；\n"
            "• 乳酸酸中毒（极罕见，发生率0.03/1000人年）：避免在eGFR<30、脓毒症、呼吸衰竭、大手术前使用。"
        ),
    },
    {
        "keywords": ["辛伐他汀", "他汀", "奥美拉唑", "红霉素", "横纹肌溶解"],
        "answer": (
            "【核心结论】辛伐他汀（脂溶性他汀，CYP3A4底物）与CYP3A4强抑制剂（红霉素、克拉霉素、酮康唑、伊曲康唑、"
            "奈法唑酮、HIV蛋白酶抑制剂等）存在【中高风险】相互作用，联用时辛伐他汀血药浓度升高5~10倍，"
            "横纹肌溶解风险显著增加，建议换用不经过CYP3A4代谢的他汀（普伐他汀、瑞舒伐他汀、匹伐他汀）。\n\n"
            "【相互作用分级】\n"
            "• 强抑制剂（禁忌联用）：红霉素、克拉霉素、酮康唑、伊曲康唑、泊沙康唑、伏立康唑、泰利霉素、奈法唑酮、"
            "HIV/HCV蛋白酶抑制剂、吉非贝齐 → 辛伐他汀血药浓度↑10~20倍，横纹肌溶解风险↑20倍，必须换他汀；\n"
            "• 中等抑制剂（减量联用）：地尔硫䓬、维拉帕米、胺碘酮、氨氯地平、雷诺嗪、达那唑、决奈达隆 → "
            "辛伐他汀日剂量不超过20mg，监测肌酸激酶（CK）；\n"
            "• 弱抑制剂（可用）：奥美拉唑（弱CYP3A4抑制，临床意义有限）、泮托拉唑、兰索拉唑 → 常规剂量下无需调整，"
            "但建议辛伐他汀不超40mg/日，出现肌痛及时查CK。\n\n"
            "【横纹肌溶解早期识别信号】弥漫性肌痛、肌无力、尿色加深（酱油尿）、CK>5倍ULN，"
            "一旦出现立即停用他汀，水化碱化尿液（碳酸氢钠静滴），必要时血液净化治疗。\n\n"
            "【替代方案参考】普伐他汀（经CYP2C9代谢为主，CYP3A4不参与）、瑞舒伐他汀（仅10%经CYP2C9代谢）"
            " 与上述抑制剂相互作用风险<辛伐他汀的1/10。"
        ),
    },
    {
        "keywords": ["高血压", "用药", "降压药", "首选"],
        "answer": (
            "【核心结论】原发性高血压初始用药遵循「个体化优先、低剂量起始、优选长效、必要时联合」原则，"
            "无合并症的普通高血压患者，五大类一线药物（CCB、ACEI/ARB、利尿剂、β受体阻滞剂）均可作为起始选择，"
            "但需根据合并症、人口学特征、靶器官损害情况选药。\n\n"
            "【各人群首选推荐（2023中国高血压防治指南）】\n"
            "1. 中青年单纯高血压（<65岁，无合并症）：ACEI/ARB 或 长效CCB 优先，前者改善RAAS激活，后者直接扩血管；\n"
            "2. 老年单纯收缩期高血压（≥65岁，ISH）：长效二氢吡啶类CCB（氨氯地平5mg qd、硝苯地平控释片30mg qd）"
            " 或 噻嗪类利尿剂（吲达帕胺缓释片1.5mg qd）优先，显著降低脑卒中风险；\n"
            "3. 高血压合并冠心病：β1受体阻滞剂（美托洛尔缓释片）+ ACEI/ARB + 他汀 + 阿司匹林，心率目标55~60次/分；\n"
            "4. 高血压合并心力衰竭：ACEI/ARB/ARNI + β受体阻滞剂 + 醛固酮受体拮抗剂（MRA）新三联，再加SGLT2i；\n"
            "5. 高血压合并糖尿病/慢性肾脏病（CKD1~3期）：ACEI/ARB 为基石（具有肾脏保护终点证据），"
            "eGFR<30ml/min或血钾持续>5.5mmol/L时换用非RAAS方案；\n"
            "6. 高血压合并前列腺增生（老年男性）：α1受体阻滞剂（特拉唑嗪）联合使用，兼顾降压与改善排尿症状。\n\n"
            "【联合用药原则】血压≥160/100mmHg或高于目标值20/10mmHg时，初始即应低剂量两药联合，"
            "首选单片复方制剂（SPC）如：ACEI/ARB+CCB、ACEI/ARB+利尿剂，较自由联合依从性↑30%，血压达标率↑20%。\n\n"
            "【注意】所有高血压患者均需同步生活方式干预（<5g盐/日、BMI<24、每周150min中等量有氧运动、戒烟限酒），"
            "药物治疗+生活方式两者缺一不可。"
        ),
    },
    {
        "keywords": ["布洛芬", "华法林", "对乙酰氨基酚", "退烧", "止痛"],
        "answer": (
            "【核心结论】长期服用华法林的患者，退热止痛首选【对乙酰氨基酚（扑热息痛）】，短期小剂量（≤2g/日）"
            "对华法林INR影响极小，出血风险可控；布洛芬（NSAIDs类）与华法林联用为【高风险】，显著增加上消化道出血风险（RR≈3.2），尽量避免。\n\n"
            "【机制差异】\n"
            "• 对乙酰氨基酚：主要在肝脏葡萄糖醛酸化代谢，对血小板COX-1抑制极弱（外周），不损伤胃黏膜屏障，"
            "常规剂量下对华法林抗凝强度无显著影响；但长期大剂量（>4g/日）可能轻度升高INR，需监测。\n"
            "• 布洛芬（及所有NSAIDs）：①抑制血小板COX-1→血小板聚集障碍；②直接损伤胃黏膜→溃疡/糜烂；"
            "③轻度抑制华法林代谢或置换蛋白结合→INR轻度升高；三重机制叠加使消化道出血风险跃升。\n\n"
            "【对乙酰氨基酚安全用法】成人325~650mg q6h，日剂量≤2g（华法林患者减半），连续使用不超过3天；"
            ">3天或需加量时，建议额外监测INR 1次。绝对避免超过4g/日（肝损伤阈值）。\n\n"
            "【如果必须用布洛芬等NSAIDs】（短期中重度疼痛，如术后、牙痛、痛风）：\n"
            "1. 加用PPI（奥美拉唑20mg qd 或 雷贝拉唑10mg qd）预防胃肠道损伤；\n"
            "2. 使用最短疗程（<5天）和最小有效剂量；\n"
            "3. 用药后第3、7天各监测INR 1次，INR>3.5时华法林临时减量10%~20%；\n"
            "4. 优先选择COX-2选择性抑制剂（塞来昔布200mg qd），胃肠道出血风险较布洛芬低约50%，但心血管风险需评估。\n\n"
            "【警惕出血信号】黑便、呕血、头晕乏力、皮肤瘀斑、牙龈自发出血→立即查INR+粪隐血，必要时急诊处理。"
        ),
    },
    {
        "keywords": ["硝苯地平", "美托洛尔", "联合", "降压"],
        "answer": (
            "【核心结论】硝苯地平（二氢吡啶类CCB）+ 美托洛尔（β1受体阻滞剂）是【经典优选降压联合方案】，"
            "两者机制互补、不良反应互相抵消，降压协同增效，且具有明确心血管保护证据，特别适合高血压合并冠心病/心绞痛患者。\n\n"
            "【机制互补性】\n"
            "• 硝苯地平：直接扩张外周小动脉→SBP/DBP均降，反射性交感激活（心率↑、心肌收缩力↑），可能诱发心悸、面部潮红；\n"
            "• 美托洛尔：阻断心脏β1受体→心率↓、心肌收缩力↓、心输出量↓、抑制RAAS；同时抵消硝苯地平引起的反射性交感激活；\n"
            "• 协同降压：两药分别作用于血管张力与心输出量两个血压决定因素，联合降压幅度≈两药单药之和的1.3~1.5倍（超加和效应）。\n\n"
            "【标准用法】\n"
            "• 硝苯地平控释片30mg qd 晨起空腹 + 琥珀酸美托洛尔缓释片47.5mg qd 晨起服；\n"
            "• 目标血压<140/90mmHg，合并糖尿病/CKD<130/80mmHg；\n"
            "• 2周未达标则硝苯地平控释片加量至60mg qd，或美托洛尔加量至95mg qd，或再加第三种药物（ACEI/ARB或利尿剂）。\n\n"
            "【不良反应相互抵消】\n"
            "• 硝苯地平常见踝部水肿（前毛细血管扩张）：美托洛尔轻度收缩静脉，可减轻水肿约30%；\n"
            "• 美托洛尔初期可能乏力、心动过缓：硝苯地平轻度反射性心率增加可协同使心率维持在60~70次/分理想区间。\n\n"
            "【监测】用药前及加量期每1~2周测坐位血压+心率，静息心率不低于55次/分；长期稳定后每月复查1次。"
        ),
    },
    {
        "keywords": ["奥美拉唑", "PPI", "长期", "副作用"],
        "answer": (
            "【核心结论】奥美拉唑及所有质子泵抑制剂（PPI）短期（<8周）使用安全性良好，不良反应少见；"
            "但长期（≥1年）大剂量维持使用需警惕多重潜在风险，应严格评估适应证，采用「降阶梯策略」和「最小有效剂量」原则。\n\n"
            "【明确有临床意义的长期风险（循证证据等级中~高）】\n"
            "1. 维生素B12吸收障碍（发生率↑约25%）：PPI抑制胃酸，食物结合型B12无法解离吸收，长期使用（>2年）"
            "建议每年检测血清B12，必要时补充甲钴胺500μg tid；\n"
            "2. 低镁血症（罕见但严重）：PPI抑制肠道镁主动转运TRPM6/7通道，血镁<0.7mmol/L可致手足搐搦、心律失常、癫痫，"
            "长期使用每6~12个月检测血镁；\n"
            "3. 骨质疏松与脆性骨折风险轻度升高（髋部骨折OR≈1.25~1.5）：长期高剂量（双倍常规剂量）+ 疗程>1年者，"
            "尤其老年女性需同步补钙1200mg/日 + 维生素D3 800IU/日；\n"
            "4. 肠道菌群紊乱与难辨梭菌（C.diff）感染风险增加（OR≈1.5~2）：PPI削弱胃酸灭菌屏障，住院患者尽量避免不必要PPI。\n\n"
            "【证据尚不充分/临床意义未定的风险】慢性肾脏病（CKD）进展、痴呆、社区获得性肺炎、胃癌（Hp根除后）——"
            "观察性研究有信号，但RCT未能验证因果，不构成停药指征但需权衡。\n\n"
            "【长期PPI规范管理流程】\n"
            "• 初始足量疗程：胃溃疡6~8周，十二指肠溃疡4~6周，GERD初始8周，Hp根除四联14天；\n"
            "• 疗程结束后降阶梯：改为「按需治疗」（仅症状发作时服药）或半量维持（如奥美拉唑10mg qd 或 20mg qod）；\n"
            "• 每年评估是否可停药：轻度GERD、NERD患者多数可逐渐停PPI，换用H2RA（法莫替丁）或按需胃黏膜保护剂（铝碳酸镁）。"
        ),
    },
    {
        "keywords": ["氢氯噻嗪", "利尿剂", "低钾", "高尿酸"],
        "answer": (
            "【核心结论】氢氯噻嗪（噻嗪类利尿剂）是高血压一线基础用药之一，价格低廉、降压确切（尤其老年ISH和盐敏感高血压），"
            "但治疗窗较窄，长期使用需重点监测和防控【低钾血症】与【高尿酸血症】两大经典不良反应。\n\n"
            "【低钾血症机制与防控】\n"
            "• 机制：噻嗪类抑制远曲小管Na+-Cl-共转运体→Na+重吸收减少→流至集合管的Na+增加→K+-Na+交换代偿性增加→K+经尿丢失；"
            "同时容量减少激活RAAS，醛固酮升高进一步促K+排泌。\n"
            "• 发生率：氢氯噻嗪25mg/日约15%~20%发生轻度低钾（K+3.0~3.5mmol/L），<1%发生严重低钾（<3.0mmol/L）。\n"
            "• 防控措施：①起始剂量12.5mg qd（小剂量优先），最大不超25mg qd；②与ACEI/ARB或螺内酯（保钾利尿剂）联合，"
            "使低钾发生率降至<3%；③多吃富钾食物（香蕉、菠菜、土豆、橙子、低脂酸奶）；④用药前、用药后1周、1个月、3个月各查血钾1次，"
            "稳定后每6个月复查；⑤K+<3.5mmol/L时口服补达秀（氯化钾缓释片）1~2g tid，K+<3.0mmol/L或伴心律失常者静脉补钾+心电监护。\n\n"
            "【高尿酸血症与痛风】\n"
            "• 机制：噻嗪类经有机酸转运体排入肾小管，竞争性抑制尿酸排泄，使血尿酸升高10%~20%，原有高尿酸血症/痛风者可诱发急性发作。\n"
            "• 防控：①有痛风病史者【避免】使用噻嗪类利尿剂，换用CCB或ACEI/ARB（氯沙坦有轻度促尿酸排泄作用，首选）；\n"
            "②必须使用时，多饮水（2~3L/日）、碱化尿液（碳酸氢钠1g tid 维持尿pH 6.2~6.8）；③血尿酸>480μmol/L且合并心血管危险因素时，"
            "启动别嘌醇或非布司他降尿酸治疗。\n\n"
            "【其他需关注】血糖轻度升高（抑制胰岛素释放，长期使用糖尿病风险轻度↑）、血脂轻度异常（LDL-C↑5%~8%）——"
            "均在小剂量下临床意义有限，但已有代谢综合征者需监测相关指标。"
        ),
    },
]


class MockLLM(LLMClient):
    def __init__(self):
        self.token_delay = 0.015
        logger.info("[MockLLM] Initialized with 10 built-in QA pairs")

    def _match_answer(self, query: str) -> str:
        q = query.strip()
        for pair in MOCK_QA_PAIRS:
            if any(kw in q for kw in pair["keywords"]):
                return pair["answer"]
        fallback = (
            f"【智能问答辅助说明】您的问题为「{q}」，目前内置演示模式下未匹配到标准知识库问答对。\n\n"
            "请尝试以下典型问题以体验完整 Graph RAG 流程：\n"
            "1. 华法林和阿司匹林能同服吗？\n"
            "2. 吃卡托普利一直干咳怎么办？\n"
            "3. 左氧氟沙星和茶碱联用有什么风险？\n"
            "4. 二甲双胍为什么是糖尿病首选药？\n"
            "5. 辛伐他汀和红霉素一起吃危险吗？\n"
            "6. 高血压患者首选什么降压药？\n"
            "7. 吃华法林的人发烧了，用布洛芬还是对乙酰氨基酚？\n"
            "8. 硝苯地平联合美托洛尔降压好吗？\n"
            "9. 奥美拉唑能长期吃吗？\n"
            "10. 氢氯噻嗪为什么会低钾？\n\n"
            "接入真实 LLM API Key 后，本系统将基于检索到的知识图谱 + 向量文档 + 数仓指标，为任意医学问题生成严谨溯源回答。"
        )
        return fallback

    async def chat_completion(
        self, messages, stream: bool = False
    ):
        last_user_content = ""
        for m in reversed(messages):
            if m.role == "user":
                last_user_content = m.content
                break
        answer_text = self._match_answer(last_user_content)

        if not stream:
            chunks = []
            for ch in answer_text:
                chunks.append(ch)
            result = "".join(chunks)
            yield result
            return

        for ch in answer_text:
            time.sleep(self.token_delay)
            yield ch


class OpenAICompatibleLLM(LLMClient):
    def __init__(self):
        from openai import AsyncOpenAI
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        logger.info(f"[OpenAICompatibleLLM] Initialized model={self.model}")

    async def chat_completion(
        self, messages, stream: bool = False
    ):
        api_messages = [{"role": m.role, "content": m.content} for m in messages]

        if not stream:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False,
            )
            content = resp.choices[0].message.content or ""
            yield content
            return

        stream_resp = await self.client.chat.completions.create(
            model=self.model,
            messages=api_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )
        async for chunk in stream_resp:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta


_llm_client = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is not None:
        return _llm_client

    settings = get_settings()
    use_mock = settings.USE_MOCK_LLM or not settings.OPENAI_API_KEY

    if use_mock:
        logger.info(f"[LLMClient] Using MockLLM (USE_MOCK_LLM={settings.USE_MOCK_LLM}, key_set={bool(settings.OPENAI_API_KEY)})")
        _llm_client = MockLLM()
    else:
        try:
            _llm_client = OpenAICompatibleLLM()
        except Exception as e:
            logger.warning(f"[LLMClient] OpenAI client init failed ({e}), fallback to MockLLM")
            _llm_client = MockLLM()
    return _llm_client
