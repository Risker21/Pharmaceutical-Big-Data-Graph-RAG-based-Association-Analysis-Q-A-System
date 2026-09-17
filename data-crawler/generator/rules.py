from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "ods_raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CORE_DRUGS = [
    {"name": "卡托普利",   "class": "ACEI",       "indication": ["高血压","心力衰竭","心肌梗死后"],
     "contra": ["ACEI过敏","双侧肾动脉狭窄","妊娠"], "adverse": ["干咳10%~20%","皮疹","味觉异常","首剂低血压"],
     "ingredients": [("卡托普利", "25mg/片")], "approval_no": "国药准字H10000001"},
    {"name": "依那普利",   "class": "ACEI",       "indication": ["高血压","心力衰竭"],
     "contra": ["ACEI过敏","双侧肾动脉狭窄","妊娠"], "adverse": ["干咳","高钾血症"],
     "ingredients": [("马来酸依那普利", "10mg/片")], "approval_no": "国药准字H10000002"},
    {"name": "二甲双胍",   "class": "Biguanide",  "indication": ["2型糖尿病"],
     "contra": ["严重肾功不全","乳酸酸中毒史","造影前后48h"], "adverse": ["胃肠道反应","维生素B12缺乏"],
     "ingredients": [("盐酸二甲双胍", "0.5g/片")], "approval_no": "国药准字H10000003"},
    {"name": "格列美脲",   "class": "Sulfonylurea","indication": ["2型糖尿病"],
     "contra": ["磺脲类过敏","1型糖尿病","酮症酸中毒"], "adverse": ["低血糖","体重增加"],
     "ingredients": [("格列美脲", "2mg/片")], "approval_no": "国药准字H10000004"},
    {"name": "阿司匹林",   "class": "Antiplatelet","indication": ["冠心病","心梗二级预防","房颤栓塞预防"],
     "contra": ["活动性出血","阿司匹林过敏","严重胃溃疡"], "adverse": ["胃肠道损伤","出血风险","瑞氏综合征儿童禁用"],
     "ingredients": [("乙酰水杨酸", "100mg/片")], "approval_no": "国药准字H10000005"},
    {"name": "华法林",     "class": "Anticoagulant_VKA","indication": ["心房颤动","深静脉血栓","机械瓣术后"],
     "contra": ["活动性出血","先兆流产","严重高血压>180/110"], "adverse": ["出血（颅内/消化道）","皮肤坏死"],
     "ingredients": [("华法林钠", "2.5mg/片")], "approval_no": "国药准字H10000006"},
    {"name": "左氧氟沙星", "class": "Quinolone",  "indication": ["呼吸道感染","泌尿系统感染","胃肠道感染"],
     "contra": ["喹诺酮过敏","18岁以下","妊娠哺乳"], "adverse": ["肌腱炎/断裂","QT间期延长","中枢兴奋","光毒性"],
     "ingredients": [("左氧氟沙星", "0.5g/片")], "approval_no": "国药准字H10000007"},
    {"name": "茶碱",       "class": "Methylxanthine","indication": ["慢性支气管炎","哮喘","COPD"],
     "contra": ["茶碱中毒史","未控制的心律失常"], "adverse": ["心律失常","恶心呕吐","失眠","惊厥"],
     "ingredients": [("茶碱", "0.1g/片")], "approval_no": "国药准字H10000008"},
    {"name": "奥美拉唑",   "class": "PPI",        "indication": ["胃溃疡","十二指肠溃疡","胃食管反流","Hp根除"],
     "contra": ["PPI过敏"], "adverse": ["头痛","腹泻","长期用低镁/维生素B12缺乏"],
     "ingredients": [("奥美拉唑", "20mg/胶囊")], "approval_no": "国药准字H10000009"},
    {"name": "辛伐他汀",   "class": "Statin",     "indication": ["高脂血症","冠心病一级二级预防"],
     "contra": ["活动性肝病","妊娠","CYP3A4强抑制剂合用"], "adverse": ["肌肉痛","肝酶升高","横纹肌溶解(罕见)"],
     "ingredients": [("辛伐他汀", "20mg/片")], "approval_no": "国药准字H10000010"},
    {"name": "硝苯地平",   "class": "CCB",        "indication": ["高血压","冠心病心绞痛"],
     "contra": ["CCB过敏","心源性休克"], "adverse": ["踝部水肿","头痛","面部潮红","心悸"],
     "ingredients": [("硝苯地平", "30mg/缓释片")], "approval_no": "国药准字H10000011"},
    {"name": "美托洛尔",   "class": "BetaBlocker","indication": ["高血压","冠心病","心力衰竭","房颤心室率控制"],
     "contra": ["二度以上房室传导阻滞","哮喘急性发作","严重心动过缓<50次/分"], "adverse": ["乏力","心动过缓","支气管痉挛"],
     "ingredients": [("酒石酸美托洛尔", "50mg/片")], "approval_no": "国药准字H10000012"},
    {"name": "氢氯噻嗪",   "class": "ThiazideDiuretic","indication": ["高血压","水肿","心力衰竭"],
     "contra": ["磺胺过敏","无尿"], "adverse": ["低钾","低钠","高尿酸","高血糖"],
     "ingredients": [("氢氯噻嗪", "25mg/片")], "approval_no": "国药准字H10000013"},
    {"name": "对乙酰氨基酚","class": "Antipyretic_Analgesic","indication": ["感冒发热","轻中度疼痛","骨关节炎"],
     "contra": ["严重肝肾功能不全","对本品过敏"], "adverse": ["肝损伤(过量>4g/日)","皮疹(罕见)"],
     "ingredients": [("对乙酰氨基酚", "0.5g/片")], "approval_no": "国药准字H10000014"},
    {"name": "布洛芬",     "class": "NSAID",      "indication": ["感冒发热","头痛","痛经","骨关节炎急性发作"],
     "contra": ["活动性溃疡","NSAID过敏","冠脉搭桥围手术期"], "adverse": ["胃肠道反应","肾损伤","心血管风险"],
     "ingredients": [("布洛芬", "0.2g/胶囊")], "approval_no": "国药准字H10000015"},
]

CORE_DISEASES = [
    ("高血压",        "I10",    "心内科",   ["头晕","头痛","颈项板紧","心悸"],   ["CCB","ACEI","ARB","BetaBlocker","利尿剂"]),
    ("2型糖尿病",     "E11",    "内分泌科", ["多饮","多尿","多食","体重下降","低血糖"], ["Biguanide","Sulfonylurea","SGLT2i","GLP1RA","胰岛素"]),
    ("冠心病",        "I25",    "心内科",   ["胸闷","胸痛","劳力性心绞痛","出汗"], ["Antiplatelet(阿司匹林)","Statin","BetaBlocker","CCB","硝酸酯类"]),
    ("心房颤动",      "I48",    "心内科",   ["心悸","胸闷","头晕","晕厥"],         ["BetaBlocker(美托洛尔)控制心率","华法林/NOAC 抗凝"]),
    ("慢性支气管炎",  "J44",    "呼吸内科", ["慢性咳嗽","咳痰","活动后气短","喘息"], ["Methylxanthine(茶碱)","吸入SABA/LABA/ICS","喹诺酮抗感染"]),
    ("胃溃疡",        "K25",    "消化内科", ["周期性上腹痛","反酸","黑便","呕血"],   ["PPI(奥美拉唑)","Hp根除铋剂+两种抗生素"]),
    ("高脂血症",      "E78",    "内分泌科", ["黄色瘤","动脉粥样硬化","多无明显症状"],["Statin(辛伐他汀)","依折麦布","PCSK9i"]),
    ("偏头痛",        "G43",    "神经内科", ["搏动性头痛","畏光畏声","恶心呕吐"],   ["NSAIDs(布洛芬)","曲坦类","对乙酰氨基酚"]),
    ("感冒",          "J00",    "全科",     ["发热","咽痛","咳嗽","鼻塞流涕","肌痛"],["休息+补水+Antipyretic_Analgesic(对乙酰氨基酚/布洛芬)"]),
    ("骨关节炎",      "M17",    "骨科/风湿",["关节疼痛","活动后加重","关节僵硬","肿胀"],["NSAIDs(布洛芬/对乙酰氨基酚)","氨基葡萄糖","关节腔注射"]),
]

CORE_INGREDIENTS = [
    ("ING01","卡托普利",217.29),("ING02","马来酸依那普利",492.52),("ING03","盐酸二甲双胍",165.63),
    ("ING04","格列美脲",490.6),("ING05","乙酰水杨酸",180.16),("ING06","华法林钠",330.3),
    ("ING07","左氧氟沙星",361.37),("ING08","茶碱",180.17),("ING09","奥美拉唑",345.42),
    ("ING10","辛伐他汀",418.57),("ING11","硝苯地平",346.34),("ING12","酒石酸美托洛尔",684.82),
    ("ING13","氢氯噻嗪",297.74),("ING14","对乙酰氨基酚",151.16),("ING15","布洛芬",206.28),
    ("ING16","螺内酯",416.57),("ING17","红霉素",733.94),("ING18","氨氯地平",408.88),
]

CORE_SYMPTOMS = [
    ("干咳","ACEI类特征性不良反应，多为刺激性无痰咳"),
    ("水肿","CCB常见踝部水肿或心衰体循环淤血"),
    ("低血糖","磺脲类/胰岛素降糖药最常见的严重不良反应"),
    ("出血风险","抗凝/抗血小板联用最核心安全警戒"),
    ("心律失常","茶碱过量、喹诺酮QT延长常见"),
    ("胃肠道反应","NSAIDs/二甲双胍常见，多为恶心呕吐腹泻"),
    ("肌肉痛","他汀类典型肌病，需监测CK"),
    ("头晕","降压药首剂低血压/低血糖常见表现"),
]

INTERACTION_RULES = [
    {
        "classes": (["Anticoagulant_VKA"], ["Antiplatelet"]),
        "level": "High",
        "risk_detail": "两类药物均影响凝血系统，联用使出血事件（消化道/颅内）发生率升高 2~3 倍，不建议常规联用（ACS+机械瓣经专科评估除外）。需监测 INR 2.0~3.0。",
        "case_count_base": 1000,
    },
    {
        "classes": (["Quinolone"], ["Methylxanthine"]),
        "level": "High",
        "risk_detail": "喹诺酮抑制 CYP1A2 酶代谢茶碱，茶碱血药浓度升高 2~4 倍可致心律失常/惊厥。建议联用时监测茶碱谷浓度并减量 50%。",
        "case_count_base": 800,
    },
    {
        "classes": (["NSAID"], ["Anticoagulant_VKA"]),
        "level": "High",
        "risk_detail": "NSAIDs 抑制血小板+损伤胃黏膜屏障，叠加华法林显著增加上消化道出血风险（RR≈3.2）。应使用 PPI 预防或改用对乙酰氨基酚。",
        "case_count_base": 700,
    },
    {
        "classes": (["ACEI"], ["Spironolactone_like"]),
        "level": "Medium",
        "risk_detail": "RAAS 双重阻断协同升高血钾，GFR<60 时高钾血症风险显著增加，每周监测血钾保持<5.0mmol/L。",
        "case_count_base": 400,
    },
    {
        "classes": (["Statin"], ["CYP3A4_Inhibitor"]),
        "level": "Medium",
        "risk_detail": "CYP3A4 强抑制剂升高他汀血药浓度 5~10 倍，增加横纹肌溶解风险。换用普伐他汀/瑞舒伐他汀或降低他汀剂量。",
        "case_count_base": 300,
    },
    {
        "classes": (["Antipyretic_Analgesic"], ["Antipyretic_Analgesic"]),
        "level": "High",
        "risk_detail": "同种对乙酰氨基酚不同复方制剂重复使用常导致肝损伤（成人>4g/日即超量），需核对所有服用药物的对乙酰氨基酚含量。",
        "case_count_base": 600,
        "same_class_only": True,
    },
]

CYP3A4_INHIBITORS = {"奥美拉唑", "红霉素"}
SPIRO_LIKE = {"螺内酯"}

DOSAGE_FORMS = ["普通片", "缓释片", "控释片", "胶囊", "肠溶胶囊", "分散片"]
DEPT_TEMPLATES = ["心内科", "内分泌科", "神经内科", "呼吸内科", "消化内科", "骨科/风湿", "全科", "血液科"]
