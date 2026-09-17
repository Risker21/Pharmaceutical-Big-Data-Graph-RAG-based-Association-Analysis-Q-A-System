import csv
import json
import hashlib
import random
from pathlib import Path

random.seed(42)

SAMPLE_DIR = Path(__file__).resolve().parent

CORE_DRUGS = [
    {"drug_id": "DR001", "name": "卡托普利", "approval_no": "国药准字H10000001", "dosage_form": "普通片", "spec": "25mg/片",
     "usage": "口服，每日3次，餐前1小时服用，初始剂量12.5mg，按需加量至50mg tid",
     "adverse_reaction": "干咳10%~20%；皮疹；味觉异常；首剂低血压",
     "contraindication_text": "ACEI过敏；双侧肾动脉狭窄；妊娠；高钾血症>6.0mmol/L",
     "pharmacology_text": "血管紧张素转换酶抑制剂(ACEI)，抑制RAAS系统，扩张血管降压，改善心室重构"},
    {"drug_id": "DR002", "name": "依那普利", "approval_no": "国药准字H10000002", "dosage_form": "普通片", "spec": "10mg/片",
     "usage": "口服，每日1~2次，起始5mg qd，维持10~20mg/日",
     "adverse_reaction": "干咳；高钾血症；头晕；乏力",
     "contraindication_text": "ACEI过敏；双侧肾动脉狭窄；妊娠；血管神经性水肿史",
     "pharmacology_text": "前体药物，经肝酯酶水解为依那普利拉，长半衰期ACEI，24h平稳降压"},
    {"drug_id": "DR003", "name": "二甲双胍", "approval_no": "国药准字H10000003", "dosage_form": "普通片", "spec": "0.5g/片",
     "usage": "口服，餐中或餐后即服，起始0.5g bid，渐加至2g/日",
     "adverse_reaction": "胃肠道反应（恶心、腹泻、腹胀）；维生素B12缺乏；乳酸酸中毒（罕见）",
     "contraindication_text": "GFR<30ml/min；乳酸酸中毒史；造影前后48h；急性代谢性酸中毒",
     "pharmacology_text": "双胍类降糖药，抑制肝糖异生，增加外周组织胰岛素敏感性，不刺激胰岛素分泌"},
    {"drug_id": "DR004", "name": "格列美脲", "approval_no": "国药准字H10000004", "dosage_form": "普通片", "spec": "2mg/片",
     "usage": "口服，早餐前或早餐时顿服，起始1~2mg qd，最大6mg/日",
     "adverse_reaction": "低血糖；体重增加；胃肠道不适；肝酶升高（罕见）",
     "contraindication_text": "磺脲类或磺胺过敏；1型糖尿病；酮症酸中毒；妊娠哺乳",
     "pharmacology_text": "第三代磺脲类促泌剂，结合胰岛β细胞KATP通道促进胰岛素释放，部分胰外增敏作用"},
    {"drug_id": "DR005", "name": "阿司匹林", "approval_no": "国药准字H10000005", "dosage_form": "肠溶片", "spec": "100mg/片",
     "usage": "口服，肠溶片餐前30min温水送服，抗血小板75~100mg qd长期维持",
     "adverse_reaction": "胃肠道黏膜损伤；出血风险增高；瑞氏综合征（儿童病毒感染禁用）；哮喘加重",
     "contraindication_text": "活动性出血；阿司匹林过敏/NSAIDs哮喘；严重活动性溃疡；严重肝肾衰竭；妊娠末3月",
     "pharmacology_text": "不可逆抑制COX-1，阻断TXA2合成，抗血小板聚集；大剂量解热镇痛抗炎"},
    {"drug_id": "DR006", "name": "华法林", "approval_no": "国药准字H10000006", "dosage_form": "普通片", "spec": "2.5mg/片",
     "usage": "口服，个体化滴定剂量，INR目标2.0~3.0（机械瓣2.5~3.5），起始2.5mg qd起始，根据INR调整",
     "adverse_reaction": "出血（颅内、消化道、皮下黏膜）；皮肤坏死（罕见，蛋白C/S缺乏者）；皮肤紫趾综合征",
     "contraindication_text": "活动性出血；先兆流产；未控制的重度高血压>180/110；近期CNS手术/创伤",
     "pharmacology_text": "维生素K拮抗剂，抑制VKORC1还原酶，阻断II/VII/IX/X凝血因子羧化激活，半衰期约40h"},
    {"drug_id": "DR007", "name": "左氧氟沙星", "approval_no": "国药准字H10000007", "dosage_form": "普通片", "spec": "0.5g/片",
     "usage": "口服，0.5g qd顿服，多饮水避免阳光直射防光毒性",
     "adverse_reaction": "肌腱炎/肌腱断裂（跟腱多见）；QT间期延长；中枢兴奋失眠；光敏反应；血糖紊乱",
     "contraindication_text": "喹诺酮类过敏；18岁以下软骨损伤；妊娠哺乳；QT间期延长先天或合用Ia/III类抗心律失常",
     "pharmacology_text": "第三代氟喹诺酮，抑制DNA旋转酶/拓扑异构酶IV，广谱G+/G-/非典型病原体覆盖"},
    {"drug_id": "DR008", "name": "茶碱", "approval_no": "国药准字H10000008", "dosage_form": "普通片", "spec": "0.1g/片",
     "usage": "口服，0.1~0.2g tid，餐后服；缓释剂型qd或bid；血药浓度窗窄，需监测5~15μg/ml",
     "adverse_reaction": "心律失常（心动过速/房颤）；恶心呕吐；失眠惊厥；心动过速；多尿",
     "contraindication_text": "茶碱中毒史；未控制的心律失常；活动性消化溃疡；未经控制的惊厥性疾病",
     "pharmacology_text": "甲基黄嘌呤类，抑制PDE升高cAMP，支气管扩张+呼吸肌兴奋+轻度抗炎；有效血药浓度10~20mg/L"},
    {"drug_id": "DR009", "name": "奥美拉唑", "approval_no": "国药准字H10000009", "dosage_form": "肠溶胶囊", "spec": "20mg/胶囊",
     "usage": "口服，晨起餐前30min整粒吞服，胃溃疡20mg qd×4~8周，Hp根除20mg bid+铋剂+两抗生素",
     "adverse_reaction": "头痛；腹泻；长期PPI相关艰难梭菌感染风险；低镁血症；维生素B12/钙吸收下降",
     "contraindication_text": "苯并咪唑类过敏；合用奈非那韦；氯吡格雷抗血小板疗效减弱警示",
     "pharmacology_text": "质子泵抑制剂PPI，不可逆抑制H+/K+-ATP酶，强效抑酸；前体药，酸环境激活共价结合"},
    {"drug_id": "DR010", "name": "辛伐他汀", "approval_no": "国药准字H10000010", "dosage_form": "普通片", "spec": "20mg/片",
     "usage": "口服，晚间顿服，起始10~20mg qn，目标LDL-C降幅30~40%，最大40mg/日",
     "adverse_reaction": "肌痛肌病（CK升高）；肝酶ALT/AST升高>3ULN需停药；横纹肌溶解（罕见但严重）",
     "contraindication_text": "活动性肝病或转氨酶持续不明原因升高；妊娠；哺乳；CYP3A4强抑制剂合用",
     "pharmacology_text": "HMG-CoA还原酶抑制剂，竞争性阻断胆固醇合成限速酶，上调LDL受体；前体药，内酯型"},
    {"drug_id": "DR011", "name": "硝苯地平", "approval_no": "国药准字H10000011", "dosage_form": "缓释片", "spec": "30mg/缓释片",
     "usage": "口服，缓释片整片吞服不可掰开，30mg qd起始，最大90mg/日",
     "adverse_reaction": "踝部水肿；面部潮红；头痛心悸；牙龈增生；反射性心动过速",
     "contraindication_text": "二氢吡啶类CCB过敏；心源性休克；近期急性心梗4周内",
     "pharmacology_text": "二氢吡啶类钙通道阻滞剂，阻滞L型Ca2+通道血管平滑肌松弛，扩张外周动脉降压"},
    {"drug_id": "DR012", "name": "美托洛尔", "approval_no": "国药准字H10000012", "dosage_form": "普通片", "spec": "50mg/片",
     "usage": "口服，平片bid，起始12.5~50mg bid；缓释片qd，晨起整片吞服，最大200mg/日。长期心衰滴定慢加量",
     "adverse_reaction": "乏力倦怠；心动过缓HR<50需评估；肢端发冷；支气管痉挛；糖脂代谢轻度影响",
     "contraindication_text": "二度及以上房室传导阻滞（无起搏器）；哮喘急性发作；失代偿性心衰；窦性心动过缓<50",
     "pharmacology_text": "选择性β1受体阻滞剂，心脏选择性抑制心率↓、收缩力↓、传导↓、肾素释放↓，抗缺血降压抗心律失常"},
    {"drug_id": "DR013", "name": "氢氯噻嗪", "approval_no": "国药准字H10000013", "dosage_form": "普通片", "spec": "25mg/片",
     "usage": "口服，晨起服避免夜尿，降压12.5~25mg qd，降压联合ACEI/ARB协同",
     "adverse_reaction": "低钾血症（K+<3.5需补钾或保钾药；高尿酸血症/痛风加重；血糖血脂轻度异常；低钠血症",
     "contraindication_text": "磺胺类交叉过敏；无尿症；严重低容量性低钠；顽固性低钾",
     "pharmacology_text": "噻嗪类利尿剂，抑制远曲小管Na+/Cl-共转运体，排钠排水降压，初始降压"},
    {"drug_id": "DR014", "name": "对乙酰氨基酚", "approval_no": "国药准字H10000014", "dosage_form": "普通片", "spec": "0.5g/片",
     "usage": "口服，成人0.3~0.6g q6h，24h≤4g；退热连用≤3天，镇痛≤5天，避免同服含对乙酰氨基酚复方制剂重复用药",
     "adverse_reaction": "肝损伤（过量>4g/日，严重肝坏死）；皮疹罕见过敏；肾损伤少见",
     "contraindication_text": "严重肝肾功能不全；对本品过敏；G6PD缺乏相对禁忌",
     "pharmacology_text": "苯胺类解热镇痛药，抑制中枢COX，外周弱，解热镇痛强，几乎无抗炎抗风湿作用，几无胃肠刺激"},
    {"drug_id": "DR015", "name": "布洛芬", "approval_no": "国药准字H10000015", "dosage_form": "胶囊", "spec": "0.2g/胶囊",
     "usage": "口服，餐中服减少胃肠刺激，镇痛0.2~0.4g q4~6h，每日≤2.4g",
     "adverse_reaction": "胃肠道刺激溃疡出血；水钠潴留水肿；肾功能不全风险心血管事件升高；肾损伤NSAIDs肾病；",
     "contraindication_text": "活动性消化溃疡出血；NSAIDs过敏史（哮喘+鼻息肉；CABG围手术期；妊娠30周后",
     "pharmacology_text": "丙酸类NSAID，抑制COX-1/2非选择性，解热镇痛抗炎，抑制血小板功能轻度可逆"},
    {"drug_id": "DR016", "name": "螺内酯", "approval_no": "国药准字H10000016", "dosage_form": "普通片", "spec": "25mg/片",
     "usage": "口服，保钾利尿剂，25~100mg/日分服，心衰加量谨慎监测血钾",
     "adverse_reaction": "高钾血症；男性乳房发育；女性月经紊乱；性功能障碍",
     "contraindication_text": "高钾血症>5.5；严重肾衰无尿；Addison病；合用ACEI/ARB+补钾剂需极度谨慎",
     "pharmacology_text": "醛固酮受体拮抗剂，竞争性结合MR受体阻断钠排钾保镁，心衰RAAS终末器官保护"},
]

CORE_DISEASES = [
    {"disease_id": "DI001", "name": "高血压", "icd_code": "I10", "department": "心内科",
     "description": "以体循环动脉压持续升高为特征的慢性心血管疾病，收缩压≥140mmHg或舒张压≥90mmHg"},
    {"disease_id": "DI002", "name": "2型糖尿病", "icd_code": "E11", "department": "内分泌科",
     "description": "以胰岛素抵抗为主伴相对胰岛素不足，或胰岛素分泌不足为主伴胰岛素抵抗的慢性代谢病"},
    {"disease_id": "DI003", "name": "冠心病", "icd_code": "I25", "department": "心内科",
     "description": "冠状动脉粥样硬化使管腔狭窄/闭塞，或冠脉痉挛致心肌缺血缺氧坏死的缺血性心脏病"},
    {"disease_id": "DI004", "name": "心房颤动", "icd_code": "I48", "department": "心内科",
     "description": "心房电活动紊乱，心房丧失规律有序的P波消失代之以快速无序的颤动波，心律绝对不齐"},
    {"disease_id": "DI005", "name": "慢性支气管炎", "icd_code": "J44", "department": "呼吸内科",
     "description": "气管支气管黏膜及其周围组织慢性非特异性炎症，每年咳嗽咳痰3月以上连续2年"},
    {"disease_id": "DI006", "name": "胃溃疡", "icd_code": "K25", "department": "消化内科",
     "description": "胃黏膜被胃消化液自身消化造成超过黏膜肌层的组织缺损，幽门螺杆菌感染主因"},
    {"disease_id": "DI007", "name": "高脂血症", "icd_code": "E78", "department": "内分泌科",
     "description": "血脂代谢异常，总胆固醇TC≥6.2或LDL-C≥4.1或TG≥2.3mmol/L"},
    {"disease_id": "DI008", "name": "偏头痛", "icd_code": "G43", "department": "神经内科",
     "description": "常见慢性神经血管性头痛，单侧搏动性中重度疼痛，畏光畏声，活动加重，持续4-72小时"},
    {"disease_id": "DI009", "name": "感冒", "icd_code": "J00", "department": "全科",
     "description": "急性上呼吸道病毒感染，鼻病毒、冠状病毒多见，自限性7-10天"},
    {"disease_id": "DI010", "name": "骨关节炎", "icd_code": "M17", "department": "骨科/风湿免疫科",
     "description": "关节软骨退行性变继发骨质增生，中老年常见，负重关节好发膝髋手脊柱"},
    {"disease_id": "DI011", "name": "心力衰竭", "icd_code": "I50", "department": "心内科",
     "description": "心脏结构或功能异常致心室射血/充盈受损，肺循环体循环淤血组织灌注不足"},
    {"disease_id": "DI012", "name": "哮喘", "icd_code": "J45", "department": "呼吸内科",
     "description": "气道慢性炎症异质性疾病，可逆性气流受限，气道高反应性，喘息气急胸闷咳嗽"},
]

CORE_SYMPTOMS = [
    {"symptom_id": "SY001", "name": "头晕", "description": "感觉周围环境或自身旋转晃动的主观感受，眩晕/头昏/站立不稳感。高血压、低血压、低血糖、贫血均可诱发"},
    {"symptom_id": "SY002", "name": "头痛", "description": "头部眉弓、耳轮上缘、枕外隆突连线以上部位的疼痛，搏动性、压迫感、紧箍感"},
    {"symptom_id": "SY003", "name": "咳嗽", "description": "呼吸道黏膜受刺激的防御性反射动作，干咳或咳痰，急性<3周急性，>8周慢性"},
    {"symptom_id": "SY004", "name": "心悸", "description": "自觉心跳快/强/不齐的不适感，心率快、期前收缩、房颤、心动过速"},
    {"symptom_id": "SY005", "name": "胸闷胸痛", "description": "胸部压迫感、憋闷、胸骨后疼痛，压榨样/烧灼样/针刺样，心绞痛心肌梗死需警惕ACS"},
    {"symptom_id": "SY006", "name": "发热", "description": "体温升高，口温≥37.3℃，感染性/非感染性病因"},
    {"symptom_id": "SY007", "name": "水肿", "description": "组织间隙体液异常积液，踝部水肿、下肢水肿、眼睑水肿、全身水肿"},
    {"symptom_id": "SY008", "name": "恶心呕吐", "description": "上腹不适欲吐，呕吐胃内容物，消化道疾病、药物不良反应、颅内压升高均可"},
    {"symptom_id": "SY009", "name": "低血糖反应", "description": "血糖<3.9mmol/L，心悸出汗手抖饥饿感，意识障碍严重"},
    {"symptom_id": "SY010", "name": "出血倾向", "description": "皮肤瘀点瘀斑、牙龈出血、鼻出血、黑便、血尿，凝血功能障碍"},
    {"symptom_id": "SY011", "name": "干咳", "description": "无痰或痰量极少的咳嗽，ACEI类药物特征性不良反应刺激性干咳"},
    {"symptom_id": "SY012", "name": "皮疹瘙痒", "description": "皮肤红斑丘疹风团，瘙痒过敏性药疹"},
    {"symptom_id": "SY013", "name": "肌肉酸痛", "description": "骨骼肌疼痛酸胀，他汀类肌病、病毒感染肌痛"},
    {"symptom_id": "SY014", "name": "关节痛", "description": "关节部位疼痛肿胀活动受限，骨关节炎、类风湿、痛风"},
    {"symptom_id": "SY015", "name": "多饮多尿", "description": "饮水量尿量异常增加，糖尿病典型三联征"},
]

CORE_INGREDIENTS = [
    {"ingredient_id": "ING001", "name": "卡托普利", "molecular_weight": 217.29, "cas_no": "62571-86-2", "category": "ACEI"},
    {"ingredient_id": "ING002", "name": "马来酸依那普利", "molecular_weight": 492.52, "cas_no": "76095-16-4", "category": "ACEI"},
    {"ingredient_id": "ING003", "name": "盐酸二甲双胍", "molecular_weight": 165.63, "cas_no": "1115-70-4", "category": "Biguanide"},
    {"ingredient_id": "ING004", "name": "格列美脲", "molecular_weight": 490.60, "cas_no": "93479-97-1", "category": "Sulfonylurea"},
    {"ingredient_id": "ING005", "name": "乙酰水杨酸（阿司匹林）", "molecular_weight": 180.16, "cas_no": "50-78-2", "category": "Antiplatelet_NSAID"},
    {"ingredient_id": "ING006", "name": "华法林钠", "molecular_weight": 330.30, "cas_no": "129-06-6", "category": "Anticoagulant_VKA"},
    {"ingredient_id": "ING007", "name": "左氧氟沙星", "molecular_weight": 361.37, "cas_no": "100986-85-4", "category": "Quinolone"},
    {"ingredient_id": "ING008", "name": "茶碱", "molecular_weight": 180.17, "cas_no": "58-55-9", "category": "Methylxanthine"},
    {"ingredient_id": "ING009", "name": "奥美拉唑", "molecular_weight": 345.42, "cas_no": "73590-58-6", "category": "PPI"},
    {"ingredient_id": "ING010", "name": "辛伐他汀", "molecular_weight": 418.57, "cas_no": "79902-63-9", "category": "Statin"},
    {"ingredient_id": "ING011", "name": "硝苯地平", "molecular_weight": 346.34, "cas_no": "21829-25-4", "category": "CCB_Dihydropyridine"},
    {"ingredient_id": "ING012", "name": "酒石酸美托洛尔", "molecular_weight": 684.82, "cas_no": "56392-17-7", "category": "BetaBlocker_Selective"},
    {"ingredient_id": "ING013", "name": "氢氯噻嗪", "molecular_weight": 297.74, "cas_no": "58-93-5", "category": "ThiazideDiuretic"},
    {"ingredient_id": "ING014", "name": "对乙酰氨基酚", "molecular_weight": 151.16, "cas_no": "103-90-2", "category": "Antipyretic_Analgesic"},
    {"ingredient_id": "ING015", "name": "布洛芬", "molecular_weight": 206.28, "cas_no": "15687-27-1", "category": "NSAID_Propionic"},
    {"ingredient_id": "ING016", "name": "螺内酯", "molecular_weight": 416.57, "cas_no": "52-01-7", "category": "PotassiumSparing_AntiMineralocorticoid"},
    {"ingredient_id": "ING017", "name": "红霉素", "molecular_weight": 733.94, "cas_no": "114-07-8", "category": "Macrolide_Antibiotic"},
    {"ingredient_id": "ING018", "name": "氨氯地平", "molecular_weight": 408.88, "cas_no": "88150-42-9", "category": "CCB_Dihydropyridine"},
]

def _id(s):
    return "DR" + hashlib.md5(s.encode("utf-8")).hexdigest()[:8].upper()

def write_csv(fname, header, rows):
    p = SAMPLE_DIR / fname
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  ✔ {fname}  ({len(rows)} rows)")

def main():
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 50)
    print("Generating MedGraphRAG sample data (9 CSV + 1 JSON)")
    print("=" * 50)

    # 1. drugs.csv
    h = ["drug_id", "name", "approval_no", "dosage_form", "spec", "usage",
         "adverse_reaction", "contraindication_text", "pharmacology_text"]
    rows = [[d[k] for k in h] for d in CORE_DRUGS]
    write_csv("drugs.csv", h, rows)

    # 2. diseases.csv
    h = ["disease_id", "name", "icd_code", "department", "description"]
    rows = [[d[k] for k in h] for d in CORE_DISEASES]
    write_csv("diseases.csv", h, rows)

    # 3. symptoms.csv
    h = ["symptom_id", "name", "description"]
    rows = [[s[k] for k in h] for s in CORE_SYMPTOMS]
    write_csv("symptoms.csv", h, rows)

    # 4. ingredients.csv
    h = ["ingredient_id", "name", "molecular_weight", "cas_no", "category"]
    rows = [[i[k] for k in h] for i in CORE_INGREDIENTS]
    write_csv("ingredients.csv", h, rows)

    # 5. drug_ingredient.csv (关联表: drug_id, ingredient_id, dose_ratio, is_primary)
    pairs = [
        ("DR001", "ING001", "25mg", 1), ("DR002", "ING002", "10mg", 1),
        ("DR003", "ING003", "500mg", 1), ("DR004", "ING004", "2mg", 1),
        ("DR005", "ING005", "100mg", 1), ("DR006", "ING006", "2.5mg", 1),
        ("DR007", "ING007", "500mg", 1), ("DR008", "ING008", "100mg", 1),
        ("DR009", "ING009", "20mg", 1), ("DR010", "ING010", "20mg", 1),
        ("DR011", "ING011", "30mg", 1), ("DR012", "ING012", "50mg", 1),
        ("DR013", "ING013", "25mg", 1), ("DR014", "ING014", "500mg", 1),
        ("DR015", "ING015", "200mg", 1), ("DR016", "ING016", "25mg", 1),
    ]
    write_csv("drug_ingredient.csv",
              ["drug_id", "ingredient_id", "dose_per_unit", "is_primary_ingredient"],
              list(pairs))

    # 6. drug_disease.csv (关联: drug_id, disease_id, relation_type, evidence_level, indication_rank)
    drug_disease_map = [
        ("DR001", "DI001", "TREATS", "A", 1), ("DR001", "DI011", "TREATS", "A", 2),
        ("DR001", "DI003", "TREATS", "B", 3), ("DR002", "DI001", "TREATS", "A", 1),
        ("DR002", "DI011", "TREATS", "A", 2), ("DR003", "DI002", "TREATS", "A", 1),
        ("DR004", "DI002", "TREATS", "A", 2), ("DR005", "DI003", "TREATS", "A", 1),
        ("DR005", "DI004", "TREATS", "A", 2), ("DR006", "DI004", "TREATS", "A", 1),
        ("DR006", "DI011", "TREATS", "B", 3), ("DR007", "DI005", "TREATS", "A", 1),
        ("DR007", "DI009", "TREATS", "B", 2), ("DR008", "DI005", "TREATS", "A", 1),
        ("DR008", "DI012", "TREATS", "A", 2), ("DR009", "DI006", "TREATS", "A", 1),
        ("DR010", "DI007", "TREATS", "A", 1), ("DR010", "DI003", "TREATS", "A", 2),
        ("DR011", "DI001", "TREATS", "A", 1), ("DR011", "DI003", "TREATS", "B", 2),
        ("DR012", "DI001", "TREATS", "A", 1), ("DR012", "DI003", "TREATS", "A", 2),
        ("DR012", "DI004", "TREATS", "A", 3), ("DR012", "DI011", "TREATS", "A", 4),
        ("DR013", "DI001", "TREATS", "A", 1), ("DR013", "DI011", "TREATS", "B", 2),
        ("DR014", "DI009", "TREATS", "A", 1), ("DR014", "DI008", "TREATS", "A", 2),
        ("DR014", "DI010", "TREATS", "B", 3), ("DR015", "DI008", "TREATS", "A", 1),
        ("DR015", "DI009", "TREATS", "A", 2), ("DR015", "DI010", "TREATS", "A", 3),
        ("DR016", "DI011", "TREATS", "A", 1), ("DR016", "DI001", "TREATS", "B", 2),
    ]
    write_csv("drug_disease.csv",
              ["drug_id", "disease_id", "relation_type", "evidence_level", "indication_rank"],
              list(drug_disease_map))

    # 7. disease_symptom.csv (关联: disease_id, symptom_id, frequency, severity_weight)
    disease_symptom_map = [
        ("DI001", "SY001", 0.75, 0.8), ("DI001", "SY002", 0.60, 0.7),
        ("DI001", "SY004", 0.45, 0.6), ("DI002", "SY015", 0.80, 0.9),
        ("DI002", "SY009", 0.50, 0.8), ("DI003", "SY005", 0.85, 1.0),
        ("DI003", "SY002", 0.35, 0.6), ("DI004", "SY004", 0.90, 0.9),
        ("DI004", "SY001", 0.55, 0.7), ("DI005", "SY003", 0.92, 0.9),
        ("DI005", "SY006", 0.60, 0.6), ("DI006", "SY008", 0.70, 0.8),
        ("DI006", "SY005", 0.65, 0.7), ("DI007", "SY001", 0.20, 0.4),
        ("DI008", "SY002", 0.95, 1.0), ("DI008", "SY012", 0.50, 0.6),
        ("DI009", "SY006", 0.88, 0.9), ("DI009", "SY003", 0.75, 0.7),
        ("DI010", "SY014", 0.90, 0.9), ("DI010", "SY013", 0.55, 0.6),
        ("DI011", "SY007", 0.82, 0.9), ("DI011", "SY003", 0.70, 0.8),
        ("DI011", "SY005", 0.60, 0.7), ("DI012", "SY003", 0.93, 0.95),
        ("DI012", "SY004", 0.60, 0.7),
    ]
    write_csv("disease_symptom.csv",
              ["disease_id", "symptom_id", "frequency", "severity_weight"],
              list(disease_symptom_map))

    # 8. drug_interaction.csv (关联: drug_a_id, drug_b_id, level, risk_detail, case_count)
    interactions = [
        ("DR006", "DR005", "High",
         "华法林+阿司匹林：抗凝+抗血小板双重抑制凝血系统，出血事件（消化道/颅内）发生率升高2~3倍，ACS合并机械瓣专科评估可联用，INR目标2.0~3.0并PPI预防", 1240),
        ("DR005", "DR006", "High",
         "阿司匹林+华法林：双向一致，同上", 1240),
        ("DR007", "DR008", "High",
         "左氧氟沙星+茶碱：喹诺酮抑制CYP1A2酶代谢茶碱，血药浓度升高2~4倍，可致心律失常/惊厥，联用需监测茶碱谷浓度并减量50%", 890),
        ("DR008", "DR007", "High",
         "茶碱+左氧氟沙星：双向一致，同上", 890),
        ("DR015", "DR006", "High",
         "布洛芬+华法林：NSAID抑制血小板+损伤胃黏膜，叠加华法林上消化道出血风险RR≈3.2，应使用PPI预防或改用对乙酰氨基酚", 760),
        ("DR006", "DR015", "High",
         "华法林+布洛芬：双向一致，同上", 760),
        ("DR001", "DR016", "Medium",
         "卡托普利+螺内酯：RAAS双重阻断协同升高血钾，GFR<60时高钾血症风险显著，每周监测血钾<5.0mmol/L", 430),
        ("DR016", "DR001", "Medium",
         "螺内酯+卡托普利：双向一致，同上", 430),
        ("DR002", "DR016", "Medium",
         "依那普利+螺内酯：RAAS双重阻断，同上血钾监测", 380),
        ("DR016", "DR002", "Medium",
         "螺内酯+依那普利：双向一致，同上", 380),
        ("DR010", "DR009", "Medium",
         "辛伐他汀+奥美拉唑：CYP3A4弱抑制剂奥美拉唑轻度升高他汀血药浓度2~3倍，增加肌病横纹肌溶解风险，建议换用普伐他汀或降低他汀剂量", 350),
        ("DR009", "DR010", "Medium",
         "奥美拉唑+辛伐他汀：双向一致，同上", 350),
        ("DR014", "DR014", "High",
         "对乙酰氨基酚重复用药>4g/日：同种或不同复方制剂中对乙酰氨基酚叠加，导致肝损伤肝坏死，需核对所有服用药物对乙酰氨基酚总量≤4g/24h", 680),
        ("DR006", "DR013", "Medium",
         "华法林+氢氯噻嗪：利尿剂改变凝血因子变化+利尿剂水电解质影响，需密切监测INR波动", 280),
        ("DR013", "DR006", "Medium",
         "氢氯噻嗪+华法林：双向一致，同上", 280),
        ("DR007", "DR012", "Medium",
         "左氧氟沙星+美托洛尔：喹诺酮QT延长+β阻滞剂心动过缓，心律失常风险轻度升高，老年QTc>500ms避免联用", 210),
        ("DR012", "DR007", "Medium",
         "美托洛尔+左氧氟沙星：双向一致，同上", 210),
        ("DR001", "DR013", "Low",
         "卡托普利+氢氯噻嗪：RAAS+噻嗪类：联合降压协同增强疗效，低钾风险需监测血钾，合理联用推荐", 150),
        ("DR013", "DR001", "Low",
         "氢氯噻嗪+卡托普利：双向一致，同上", 150),
        ("DR011", "DR012", "Low",
         "硝苯地平+美托洛尔：CCB+β阻滞剂：协同降压，抵消反射心动过速，推荐联合", 180),
        ("DR012", "DR011", "Low",
         "美托洛尔+硝苯地平：双向一致，同上", 180),
        ("DR003", "DR009", "Low",
         "二甲双胍+奥美拉唑：长期PPI影响B12吸收+二甲双胍B12缺乏风险叠加，建议定期监测B12", 200),
        ("DR009", "DR003", "Low",
         "奥美拉唑+二甲双胍：双向一致，同上", 200),
    ]
    write_csv("drug_interaction.csv",
              ["drug_a_id", "drug_b_id", "level", "risk_detail", "case_count"],
              list(interactions))

    # 9. side_effects.csv (第9个CSV: side_effects 药品不良反应明细)
    side_effects = []
    se_id = 1
    for d in CORE_DRUGS:
        for idx = d["adverse_reaction"]
        items = [x.strip() for x in idx.split("；") if x.strip()]
        for rank = 1
        for item in items:
            side_effects.append([
                f"SE{se_id:04d}", d["drug_id"], item,
                random.choice(["Common", "Common", "Common", "Uncommon", "Rare"]),
                round(random.uniform(0.01, 0.25), 3), rank
            ])
            se_id += 1
            rank += 1
    write_csv("side_effects.csv",
              ["side_effect_id", "drug_id", "effect_description", "frequency_category", "incidence_rate", "severity_rank"],
              side_effects)

    # 10. clinical_guidelines.json
    guidelines = []
    templates = [
        ("根据《{dept}诊疗指南（{yr}版）》，{disease}的一线治疗原则应优先选择{drug_cls}类药物，靶目标为达标治疗，强调个体化滴定和长期依从性管理。",
         "I类推荐A级证据。针对{dept学会20{yr}专家共识要点：{disease}合并{comorbidity}高危因素患者，建议初始联合{drug_cls}+{add_on}强化控制多重危险因素。",
         "用法用量规范：{drug_cls}起始低剂量起始，每2~4周评估疗效和耐受性，靶目标未达则逐步加量或联合第二药，避免突然停药导致反跳现象。",
         "安全性警戒：使用{drug_cls}期间需定期监测{monitor}指标，{monitor2。GFR<60ml/min/1.73m²者剂量减半；避免与{interact}联用存在风险。",
         "疗程随访路径：{disease}诊断明确后启动{drug_cls}治疗{m}个月评估疗效，达标后维持长期治疗，每{q}月门诊随访复查相关指标，年度综合评估。",
    ]
    drug_cls_names = {
        "DR001": "ACEI（卡托普利）", "DR002": "ACEI（依那普利）", "DR003": "双胍类（二甲双胍）",
        "DR004": "磺脲类（格列美脲）", "DR005": "抗血小板（阿司匹林）", "DR006": "VKA抗凝（华法林）",
        "DR007": "氟喹诺酮（左氧氟沙星）", "DR008": "甲基黄嘌呤（茶碱）",
        "DR009": "PPI（奥美拉唑）", "DR010": "他汀类（辛伐他汀）",
        "DR011": "CCB（硝苯地平）", "DR012": "β1阻滞剂（美托洛尔）",
        "DR013": "噻嗪利尿剂（氢氯噻嗪）", "DR014": "解热镇痛（对乙酰氨基酚）",
        "DR015": "NSAID（布洛芬）", "DR016": "醛固酮拮抗剂（螺内酯）",
    }
    monitors_pool = ["血压+心率、电解质、血钾、血肌酐eGFR", "空腹血糖、HbA1c糖化血红蛋白、肝肾功能",
                 "INR国际标准化比值、凝血功能PT、APTT", "肝酶ALT/AST、肌酸激酶CK",
                 "心电图、动态血压ABPM、超声心动图LVEF"]
    comorbidities = ["心血管高危因素（冠心病/房颤）", "糖尿病合并2型糖尿病", "老年≥75岁以上", "慢性肾病CKD3期", "高血压合并3级极高危"]
    yr_pool = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    cid = 1
    for d_idx, disease in enumerate(CORE_DISEASES):
        did, dname, icd, dept, _ = disease["disease_id"], disease["name"], disease["icd_code"], disease["department"], disease["description"]
        for tmpl_idx, tmpl in enumerate(templates):
            yr = random.choice(yr_pool)
            # 选2个关联药
            related_drugs = [r for r in drug_disease_map if r[1] == did
            if not related_drugs:
                continue
            dr = random.choice(related_drugs)
            drug_cls = drug_cls_names.get(dr[0], dr[0])
            add_on_drug = random.choice([x for x in drug_cls_names.values() if x != drug_cls][:3])
            comorbidity = random.choice(comorbidities)
            m = random.choice([1, 2, 3, 6])
            q = random.choice([1, 2, 3, 6])
            mon1, mon2 = random.sample(monitors_pool, 2)
            interact = random.choice(["CYP3A4强抑制剂", "华法林类抗凝药", "其他延长QT间期药物"])
            content = tmpl.format(
                disease=dname, dept=dept, yr=yr, drug_cls=drug_cls,
                comorbidity=comorbidity, add_on=add_on_drug,
                monitor=mon1, monitor2=mon2, m=m, q=q, interact=interact
            )
            guidelines.append({
                "chunk_id": f"GL{cid:04d}",
                "content": content,
                "source": f"中华医学会{dept}学分会《{dname}诊疗指南（{yr}年版）",
                "publish_year": yr,
                "disease_refs": [dname, icd],
                "drug_refs": [dr[0], drug_cls],
            })
            cid += 1
    with open(SAMPLE_DIR / "clinical_guidelines.json", "w", encoding="utf-8") as f:
        json.dump(guidelines, f, ensure_ascii=False, indent=2)
    print(f"  ✔ clinical_guidelines.json  ({len(guidelines)} chunks)")

    print("\n" + "=" * 50)
    print(f"[DONE: 9 CSV + 1 JSON 样本数据生成完毕")
    print("=" * 50)


if __name__ == "__main__":
    main()
