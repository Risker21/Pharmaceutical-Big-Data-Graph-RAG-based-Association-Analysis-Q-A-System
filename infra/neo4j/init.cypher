CREATE CONSTRAINT drug_name IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT disease_name IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT ingredient_name IF NOT EXISTS FOR (i:Ingredient) REQUIRE i.name IS UNIQUE;
CREATE CONSTRAINT symptom_name IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE;
CREATE INDEX drug_pagerank IF NOT EXISTS FOR (d:Drug) ON (d.pagerank);
CREATE INDEX community_id IF NOT EXISTS FOR (n) ON (n.community_id);

UNWIND [
  {name:'卡托普利', class:'ACEI', approval_no:'国药准字H10000001', spec:'25mg/片'},
  {name:'依那普利', class:'ACEI', approval_no:'国药准字H10000002', spec:'10mg/片'},
  {name:'二甲双胍', class:'Biguanide', approval_no:'国药准字H10000003', spec:'0.5g/片'},
  {name:'格列美脲', class:'Sulfonylurea', approval_no:'国药准字H10000004', spec:'2mg/片'},
  {name:'阿司匹林', class:'Antiplatelet', approval_no:'国药准字H10000005', spec:'100mg/片'},
  {name:'华法林', class:'Anticoagulant_VKA', approval_no:'国药准字H10000006', spec:'2.5mg/片'},
  {name:'左氧氟沙星', class:'Quinolone', approval_no:'国药准字H10000007', spec:'0.5g/片'},
  {name:'茶碱', class:'Methylxanthine', approval_no:'国药准字H10000008', spec:'0.1g/片'},
  {name:'奥美拉唑', class:'PPI', approval_no:'国药准字H10000009', spec:'20mg/胶囊'},
  {name:'辛伐他汀', class:'Statin', approval_no:'国药准字H10000010', spec:'20mg/片'},
  {name:'硝苯地平', class:'CCB', approval_no:'国药准字H10000011', spec:'30mg/缓释片'},
  {name:'美托洛尔', class:'BetaBlocker', approval_no:'国药准字H10000012', spec:'50mg/片'},
  {name:'氢氯噻嗪', class:'ThiazideDiuretic', approval_no:'国药准字H10000013', spec:'25mg/片'},
  {name:'对乙酰氨基酚', class:'Antipyretic_Analgesic', approval_no:'国药准字H10000014', spec:'0.5g/片'},
  {name:'布洛芬', class:'NSAID', approval_no:'国药准字H10000015', spec:'0.2g/胶囊'}
] AS d MERGE (drug:Drug {name: d.name})
  SET drug.class = d.class, drug.approval_no = d.approval_no, drug.spec = d.spec;

UNWIND [
  ['高血压','I10','心内科'],['2型糖尿病','E11','内分泌科'],['冠心病','I25','心内科'],
  ['心房颤动','I48','心内科'],['慢性支气管炎','J44','呼吸内科'],['胃溃疡','K25','消化内科'],
  ['高脂血症','E78','内分泌科'],['偏头痛','G43','神经内科'],['感冒','J00','全科'],
  ['骨关节炎','M17','骨科/风湿']
] AS t MERGE (dis:Disease {name: t[0]}) SET dis.icd_code = t[1], dis.department = t[2];

UNWIND [
  ['卡托普利',217.29],['盐酸二甲双胍',165.63],['乙酰水杨酸',180.16],['华法林钠',330.3],
  ['左氧氟沙星',361.37],['茶碱',180.17],['奥美拉唑',345.42],['辛伐他汀',418.57],
  ['硝苯地平',346.34],['酒石酸美托洛尔',684.82],['氢氯噻嗪',297.74],['对乙酰氨基酚',151.16],
  ['布洛芬',206.28],['螺内酯',416.57],['红霉素',733.94],['马来酸依那普利',492.52],
  ['格列美脲',490.6],['氨氯地平',408.88]
] AS t MERGE (i:Ingredient {name: t[0]}) SET i.molecular_weight = t[1];

UNWIND [
  ['干咳','ACEI类特征性刺激性无痰咳'],['水肿','踝部水肿或心衰淤血'],
  ['低血糖','降糖药最常见严重不良反应'],['出血风险','抗凝/抗血小板联用核心警戒'],
  ['心律失常','茶碱/喹诺酮QT延长'],['胃肠道反应','恶心呕吐腹泻'],
  ['肌肉痛','他汀类典型肌病'],['头晕','首剂低血压/低血糖']
] AS t MERGE (s:Symptom {name: t[0]}) SET s.description = t[1];

UNWIND [
  ['卡托普利','卡托普利'],['依那普利','马来酸依那普利'],['二甲双胍','盐酸二甲双胍'],
  ['格列美脲','格列美脲'],['阿司匹林','乙酰水杨酸'],['华法林','华法林钠'],
  ['左氧氟沙星','左氧氟沙星'],['茶碱','茶碱'],['奥美拉唑','奥美拉唑'],
  ['辛伐他汀','辛伐他汀'],['硝苯地平','硝苯地平'],['美托洛尔','酒石酸美托洛尔'],
  ['氢氯噻嗪','氢氯噻嗪'],['对乙酰氨基酚','对乙酰氨基酚'],['布洛芬','布洛芬']
] AS t MATCH (d:Drug {name: t[0]}), (i:Ingredient {name: t[1]})
  MERGE (d)-[:CONTAINS {dose: '按说明书'}]->(i);

UNWIND [
  ['卡托普利','高血压',0.78],['卡托普利','冠心病',0.62],['依那普利','高血压',0.80],
  ['二甲双胍','2型糖尿病',0.92],['格列美脲','2型糖尿病',0.85],
  ['阿司匹林','冠心病',0.90],['阿司匹林','心房颤动',0.75],
  ['华法林','心房颤动',0.93],['华法林','冠心病',0.45],
  ['左氧氟沙星','慢性支气管炎',0.82],['左氧氟沙星','胃溃疡',0.25],
  ['茶碱','慢性支气管炎',0.80],['茶碱','感冒',0.35],
  ['奥美拉唑','胃溃疡',0.93],['辛伐他汀','高脂血症',0.94],
  ['辛伐他汀','冠心病',0.72],['硝苯地平','高血压',0.82],
  ['美托洛尔','高血压',0.78],['美托洛尔','冠心病',0.86],
  ['氢氯噻嗪','高血压',0.72],['对乙酰氨基酚','感冒',0.90],
  ['布洛芬','感冒',0.82],['布洛芬','骨关节炎',0.90]
] AS t MATCH (d:Drug {name: t[0]}), (dis:Disease {name: t[1]})
  MERGE (d)-[:TREATS {efficacy: t[2]}]->(dis);

UNWIND [
  ['高血压','头晕',0.80],['高血压','头痛',0.75],
  ['2型糖尿病','低血糖',0.78],['2型糖尿病','头晕',0.40],
  ['冠心病','头晕',0.55],['心房颤动','心律失常',0.95],
  ['慢性支气管炎','头晕',0.20],['胃溃疡','胃肠道反应',0.90],
  ['高脂血症','肌肉痛',0.10],['感冒','头晕',0.50],
  ['骨关节炎','肌肉痛',0.85]
] AS t MATCH (dis:Disease {name: t[0]}), (s:Symptom {name: t[1]})
  MERGE (dis)-[:HAS_SYMPTOM {probability: t[2]}]->(s);

UNWIND [
  ['华法林','阿司匹林','High','两类均影响凝血，联用出血事件升高 2~3 倍，INR 2.0~3.0 严密监测',1240],
  ['阿司匹林','华法林','High','两类均影响凝血，联用出血事件升高 2~3 倍，INR 2.0~3.0 严密监测',1240],
  ['左氧氟沙星','茶碱','High','喹诺酮抑制茶碱CYP1A2代谢，茶碱血药升高2~4倍可致惊厥/心律失常，减量50%并监测谷浓度',890],
  ['茶碱','左氧氟沙星','High','喹诺酮抑制茶碱CYP1A2代谢，茶碱血药升高2~4倍可致惊厥/心律失常，减量50%并监测谷浓度',890],
  ['布洛芬','华法林','High','NSAIDs损伤胃黏膜+抑制血小板，叠加华法林使上消化道出血RR≈3.2，加用PPI或换对乙酰氨基酚',780],
  ['华法林','布洛芬','High','NSAIDs损伤胃黏膜+抑制血小板，叠加华法林使上消化道出血RR≈3.2，加用PPI或换对乙酰氨基酚',780],
  ['对乙酰氨基酚','对乙酰氨基酚','High','同种复方制剂重复使用超4g/日常致肝损伤，需核对所有用药的对乙酰氨基酚含量',650],
  ['卡托普利','螺内酯','Medium','RAAS双重阻断升血钾，GFR<60时每周监测血钾<5.0mmol/L',410],
  ['依那普利','螺内酯','Medium','RAAS双重阻断升血钾，GFR<60时每周监测血钾<5.0mmol/L',380],
  ['辛伐他汀','奥美拉唑','Medium','CYP3A4弱抑制升辛伐他汀血药，增加横纹肌溶解风险，换普伐他汀或剂量减半',320]
] AS t MATCH (a:Drug {name: t[0]}), (b:Drug {name: t[1]})
  MERGE (a)-[r:INTERACTS_WITH]->(b)
  SET r.level = t[2], r.risk_detail = t[3], r.case_count = t[4];

MATCH (n) WHERE n.pagerank IS NULL SET n.pagerank = 0.0;
MATCH (n) WHERE n.community_id IS NULL SET n.community_id = 0;
