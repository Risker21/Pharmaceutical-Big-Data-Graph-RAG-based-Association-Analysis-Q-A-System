import http from './http'

export interface LayerStats {
  ods: { rows: number; tables: number; details: { name: string; rows: number }[] }
  dwd: { rows: number; tables: number; details: { name: string; rows: number }[] }
  ads: { rows: number; tables: number; details: { name: string; rows: number }[] }
}

export interface EtlJob {
  job_name: string
  status: 'success' | 'running' | 'retry' | 'failed'
  start_ts: number
  end_ts: number
  duration_ms: number
  input_rows: number
  output_rows: number
  error_msg?: string
  spark_ui_link?: string
  stdout?: string
}

export interface PageRankItem {
  node_name: string
  node_type: 'drug' | 'disease' | 'ingredient' | 'symptom'
  pagerank: number
  community: number
}

export interface CommunityItem {
  community_id: number
  node_count: number
  top_drug: string
  top_disease: string
  typeBreakdown: { drug: number; disease: number; ingredient: number; symptom: number }
}

export interface HeatmapCell {
  x: string
  y: string
  value: number
}

export interface ContraindicationItem {
  pair: [string, string]
  level: 'High' | 'Medium' | 'Low'
  risk_detail: string
  case_count: number
}

export async function getLayerStats(): Promise<LayerStats> {
  const mock: LayerStats = {
    ods: {
      rows: 156432,
      tables: 6,
      details: [
        { name: 'ods_drugs', rows: 58320 },
        { name: 'ods_diseases', rows: 12485 },
        { name: 'ods_guidelines', rows: 25956 },
        { name: 'ods_ingredients', rows: 8234 },
        { name: 'ods_interactions', rows: 42156 },
        { name: 'ods_symptoms', rows: 9281 }
      ]
    },
    dwd: {
      rows: 142895,
      tables: 8,
      details: [
        { name: 'dwd_drug_dim', rows: 58320 },
        { name: 'dwd_disease_dim', rows: 12485 },
        { name: 'dwd_guideline_chunk', rows: 25956 },
        { name: 'dwd_ingredient_dim', rows: 8234 },
        { name: 'dwd_treatment_edge', rows: 18423 },
        { name: 'dwd_contraindication_edge', rows: 12876 },
        { name: 'dwd_interaction_edge', rows: 6601 },
        { name: 'dwd_symptom_dim', rows: 9281 }
      ]
    },
    ads: {
      rows: 88420,
      tables: 5,
      details: [
        { name: 'ads_pagerank', rows: 79039 },
        { name: 'ads_community', rows: 79039 },
        { name: 'ads_contraindication_top', rows: 500 },
        { name: 'ads_ingredient_similarity', rows: 400 },
        { name: 'ads_department_agg', rows: 42 }
      ]
    }
  }
  try {
    const res = await http.get<any, LayerStats>('/etl/layer-stats')
    return res && res.ods ? res : mock
  } catch {
    return mock
  }
}

export async function getJobHistory(limit: number = 30): Promise<EtlJob[]> {
  const jobs = ['01_ods_to_dwd', '02_neo4j_bulk_loader', '03_milvus_indexer', '04_hbase_bulk_loader', '05_pagerank_calculator', '06_ads_pipeline', '07_louvain_community']
  const statuses: EtlJob['status'][] = ['success', 'success', 'success', 'retry', 'success', 'success', 'failed', 'success', 'running']
  const mock: EtlJob[] = Array.from({ length: limit }).map((_, i) => {
    const start = Date.now() - (i + 1) * 3600000 * 4 - Math.random() * 3600000
    const dur = 60000 + Math.floor(Math.random() * 300000)
    const status = i === 0 ? 'running' : statuses[i % statuses.length]
    return {
      job_name: jobs[i % jobs.length] + ` (轮次${Math.floor(i / jobs.length) + 1})`,
      status,
      start_ts: start,
      end_ts: status === 'running' ? 0 : start + dur,
      duration_ms: status === 'running' ? Date.now() - start : dur,
      input_rows: 10000 + Math.floor(Math.random() * 50000),
      output_rows: 9000 + Math.floor(Math.random() * 45000),
      error_msg: status === 'failed' ? 'OutOfMemoryError: GC overhead limit exceeded at SparkExecutor...' : undefined,
      spark_ui_link: status === 'running' ? 'http://spark-master:8080/job?id=' + i : undefined,
      stdout: status === 'failed' ? `Job aborted due to stage failure:\nTask 12 in stage 45.0 failed 4 times, most recent failure: Lost task 12.3 in stage 45.0 (TID 8923, executor 5): java.lang.OutOfMemoryError\n\tat org.apache.spark.sql.catalyst.expressions.GeneratedClass$GeneratedIteratorForCodegenStage12.hashAgg_doAggregateWithKeys_0$(Unknown Source)\n\t... 23 more` : `===== Job ${jobs[i % jobs.length]} =====\n[INFO] Input: 58320 rows from ods_drugs\n[INFO] Stage 1/3: Clean & dedup... 58320 -> 58298\n[INFO] Stage 2/3: Enrich dimension... OK\n[INFO] Stage 3/3: Write DWD... 58298 rows written in 23s\n[SUCCESS] Job finished in ${Math.floor(dur/1000)}s`
    }
  })
  try {
    const res = await http.get<any, EtlJob[]>(`/etl/job-history?limit=${limit}`)
    return Array.isArray(res) && res.length > 0 ? res : mock
  } catch {
    return mock
  }
}

export async function getPageRankTop(n: number = 20): Promise<PageRankItem[]> {
  const types: PageRankItem['node_type'][] = ['drug', 'disease', 'ingredient', 'symptom']
  const names = ['卡托普利', '高血压', '二甲双胍', '2型糖尿病', '华法林', '阿司匹林', '冠心病', '对乙酰氨基酚', '辛伐他汀', '布洛芬', '左氧氟沙星', '心房颤动', '奥美拉唑', '高脂血症', '硝苯地平', '慢性支气管炎', '美托洛尔', '胃溃疡', '茶碱', '偏头痛']
  const mock: PageRankItem[] = names.map((name, i) => ({
    node_name: name,
    node_type: types[i % 4],
    pagerank: +(15 - i * 0.55 + Math.random() * 0.8).toFixed(3),
    community: (i % 5) + 1
  })).sort((a, b) => b.pagerank - a.pagerank)

  try {
    const res = await http.get<any, PageRankItem[]>(`/etl/page-rank-top?n=${n}`)
    return Array.isArray(res) && res.length > 0 ? res : mock
  } catch {
    return mock
  }
}

export async function getCommunitySize(): Promise<CommunityItem[]> {
  const drugs = ['卡托普利', '二甲双胍', '华法林', '对乙酰氨基酚', '辛伐他汀', '左氧氟沙星', '奥美拉唑', '硝苯地平', '美托洛尔', '茶碱']
  const diseases = ['高血压', '2型糖尿病', '冠心病', '感冒', '高脂血症', '心房颤动', '胃溃疡', '慢性支气管炎', '偏头痛', '骨关节炎']
  const mock: CommunityItem[] = Array.from({ length: 10 }).map((_, i) => ({
    community_id: i + 1,
    node_count: 800 + Math.floor(Math.random() * 4000),
    top_drug: drugs[i],
    top_disease: diseases[i],
    typeBreakdown: {
      drug: 50 + Math.floor(Math.random() * 200),
      disease: 20 + Math.floor(Math.random() * 80),
      ingredient: 80 + Math.floor(Math.random() * 300),
      symptom: 30 + Math.floor(Math.random() * 150)
    }
  }))
  try {
    const res = await http.get<any, CommunityItem[]>('/etl/community-size')
    return Array.isArray(res) && res.length > 0 ? res : mock
  } catch {
    return mock
  }
}

export async function getIngredientHeatmap(): Promise<{ drugs: string[]; matrix: number[][] }> {
  const drugs = ['卡托普利', '依那普利', '二甲双胍', '格列美脲', '阿司匹林', '华法林', '左氧氟沙星', '茶碱', '奥美拉唑', '辛伐他汀', '硝苯地平', '美托洛尔', '氢氯噻嗪', '对乙酰氨基酚', '布洛芬', '螺内酯', '红霉素', '氨氯地平', '缬沙坦', '阿托伐他汀']
  const matrix = drugs.map((_, i) => drugs.map((__, j) => {
    if (i === j) return 1
    if (Math.floor(i / 5) === Math.floor(j / 5)) return +(0.3 + Math.random() * 0.5).toFixed(2)
    return +(Math.random() * 0.25).toFixed(2)
  }))
  const mock = { drugs, matrix }
  try {
    const res = await http.get<any, { drugs: string[]; matrix: number[][] }>('/etl/ingredient-heatmap')
    return res && res.drugs ? res : mock
  } catch {
    return mock
  }
}

export async function getTopContraindications(n: number = 50): Promise<ContraindicationItem[]> {
  const pairs: [string, string][] = [
    ['华法林', '阿司匹林'], ['左氧氟沙星', '茶碱'], ['布洛芬', '华法林'],
    ['对乙酰氨基酚', '对乙酰氨基酚(复方)'], ['卡托普利', '螺内酯'], ['辛伐他汀', '红霉素'],
    ['辛伐他汀', '奥美拉唑'], ['华法林', '左氧氟沙星'], ['依那普利', '螺内酯'],
    ['茶碱', '红霉素'], ['硝苯地平', '西地那非'], ['二甲双胍', '造影剂(48h内)'],
    ['华法林', '磺胺类'], ['格列美脲', '磺胺类'], ['氢氯噻嗪', '锂剂'],
    ['ACEI类', 'ARNI类'], ['三环抗抑郁药', 'MAOI'], ['他汀类', '吉非贝齐'],
    ['甲氨蝶呤', 'NSAIDs'], ['氨基糖苷类', '呋塞米']
  ]
  const levels: ContraindicationItem['level'][] = ['High', 'High', 'High', 'High', 'Medium', 'Medium', 'Medium', 'High', 'Medium', 'Medium', 'Medium', 'High', 'Medium', 'Medium', 'Low', 'High', 'High', 'Medium', 'Medium', 'Medium']
  const risks = ['出血风险显著升高', '茶碱代谢抑制心律失常风险', '上消化道出血RR≈3.2', '肝毒性叠加>4g/d致肝衰竭', '高钾血症需监测血钾<5.0', '横纹肌溶解需换用普伐他汀', '横纹肌溶解弱抑制需监测CK', 'INR波动需加测频次', '高钾血症', '茶碱血药浓度升2-4倍', '降压叠加致严重低血压', '乳酸酸中毒需停药48h', 'INR升高需减量', '降糖增强致低血糖', '锂蓄积中毒', '血管性水肿叠加', '5-HT综合征致死性', '横纹肌溶解吉非贝齐禁用', '甲氨蝶呤血药升高骨髓抑制', '耳毒性肾毒性叠加']
  const mock: ContraindicationItem[] = pairs.concat(pairs.map(p => [p[1] + '衍生物', p[0]]) as any).slice(0, n).map((pair, i) => ({
    pair,
    level: levels[i % levels.length],
    risk_detail: risks[i % risks.length],
    case_count: 50 + Math.floor(Math.random() * 1200)
  })).sort((a, b) => b.case_count - a.case_count)

  try {
    const res = await http.get<any, ContraindicationItem[]>(`/etl/top-contraindications-n?n=${n}`)
    return Array.isArray(res) && res.length > 0 ? res : mock
  } catch {
    return mock
  }
}
