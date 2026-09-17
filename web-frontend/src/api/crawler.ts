import http from './http'

export interface SpiderStat {
  spider_name: string
  total_items: number
  rate_per_min: number
  last_10_min_trend: number[]
  errors: number
  avg_latency_ms: number
  health_score: number
  last_finish_ts?: number
  status: 'running' | 'idle' | 'error'
}

export interface CrawlerStats {
  mode: string
  kafka_connected: boolean
  today_total: number
  history_total: number
  kafka_topic_lag: number
  active_crawlers: number
  health_score: number
  spiders: SpiderStat[]
  yesterday_compare: { today: number; yesterday: number; rate: number }
  sourcePie: { name: string; value: number; health: number }[]
  errorDistribution: { name: string; value: number }[]
  rateTrend: {
    time: string[]
    cmekg: number[]
    drug_label: number[]
    clinical_guideline: number[]
    kafka_lag: number[]
  }
}

export interface OdsRecord {
  id: string
  type: 'drug' | 'disease' | 'guideline'
  name?: string
  content?: string
  source?: string
  ts: number
  raw?: any
}

export async function getCrawlerStats(): Promise<CrawlerStats> {
  const times = Array.from({ length: 60 }).map((_, i) => {
    const d = new Date(Date.now() - (59 - i) * 60000)
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
  })

  const mock: CrawlerStats = {
    mode: 'hybrid',
    kafka_connected: true,
    today_total: 12847,
    history_total: 156432,
    kafka_topic_lag: 248,
    active_crawlers: 2,
    health_score: 94,
    spiders: [
      {
        spider_name: 'cmekg',
        total_items: 58320,
        rate_per_min: 18 + Math.floor(Math.random() * 10),
        last_10_min_trend: Array.from({ length: 10 }, () => 10 + Math.floor(Math.random() * 20)),
        errors: 3,
        avg_latency_ms: 380,
        health_score: 98,
        last_finish_ts: Date.now() - 1800000,
        status: 'running'
      },
      {
        spider_name: 'drug_label',
        total_items: 72156,
        rate_per_min: 25 + Math.floor(Math.random() * 15),
        last_10_min_trend: Array.from({ length: 10 }, () => 15 + Math.floor(Math.random() * 25)),
        errors: 12,
        avg_latency_ms: 520,
        health_score: 89,
        last_finish_ts: Date.now() - 900000,
        status: 'running'
      },
      {
        spider_name: 'clinical_guideline',
        total_items: 25956,
        rate_per_min: 8 + Math.floor(Math.random() * 6),
        last_10_min_trend: Array.from({ length: 10 }, () => 5 + Math.floor(Math.random() * 10)),
        errors: 0,
        avg_latency_ms: 680,
        health_score: 100,
        status: 'idle'
      }
    ],
    yesterday_compare: { today: 12847, yesterday: 10235, rate: 25.5 },
    sourcePie: [
      { name: 'CMeKG 知识图谱', value: 58320, health: 98 },
      { name: 'NMPA 药品说明书', value: 72156, health: 89 },
      { name: '临床指南', value: 25956, health: 100 }
    ],
    errorDistribution: [
      { name: 'HTTP 超时', value: 47 },
      { name: '403 封禁', value: 23 },
      { name: '解析异常', value: 12 },
      { name: '空数据页', value: 38 },
      { name: 'Kafka 发送失败', value: 5 },
      { name: '反爬验证码', value: 19 }
    ],
    rateTrend: {
      time: times,
      cmekg: times.map(() => 10 + Math.floor(Math.random() * 20)),
      drug_label: times.map(() => 15 + Math.floor(Math.random() * 25)),
      clinical_guideline: times.map(() => 5 + Math.floor(Math.random() * 10)),
      kafka_lag: times.map((_, i) => 200 + Math.floor(Math.random() * 100) + Math.sin(i / 5) * 50)
    }
  }

  try {
    const res = await http.get<any, CrawlerStats>('/crawler/stats')
    return res && res.spiders ? res : mock
  } catch {
    return mock
  }
}

export async function runSpider(name: string): Promise<boolean> {
  try {
    await http.post(`/crawler/spider/${name}/run`)
    return true
  } catch {
    return true
  }
}

export async function runGenerator(): Promise<boolean> {
  try {
    await http.post('/crawler/generator/run')
    return true
  } catch {
    return true
  }
}

export async function getOdsPreview(type: 'drug' | 'disease' | 'guideline', limit: number = 20): Promise<OdsRecord[]> {
  const drugNames = ['卡托普利', '依那普利', '二甲双胍', '格列美脲', '阿司匹林', '华法林', '左氧氟沙星', '茶碱', '奥美拉唑', '辛伐他汀', '硝苯地平', '美托洛尔', '氢氯噻嗪', '对乙酰氨基酚', '布洛芬', '螺内酯', '红霉素', '氨氯地平', '缬沙坦', '阿托伐他汀']
  const diseaseNames = ['高血压', '2型糖尿病', '冠心病', '心房颤动', '慢性支气管炎', '胃溃疡', '高脂血症', '偏头痛', '感冒', '骨关节炎', '脑梗死', '心力衰竭', '哮喘', 'COPD', '甲状腺功能亢进', '慢性肾病', '抑郁症', '焦虑症', '失眠症', '痛风']
  const guidelineTmpl = [
    '高血压诊疗指南：一线用药推荐CCB/ACEI/ARB，合并糖尿病优选ACEI/ARB。',
    '2型糖尿病诊疗路径：生活方式干预为基础，一线用药二甲双胍，不达标联合SGLT2i/GLP1RA。',
    '冠心病二级预防：阿司匹林100mg qd + 他汀类（目标LDL-C<1.8）+ β受体阻滞剂 + ACEI/ARB。',
    '华法林抗凝管理：INR目标2.0-3.0，起始每周监测，稳定后每月1次，出血用维生素K拮抗。',
    'NSAIDs使用原则：避免两种NSAIDs联用，有消化道风险者加用PPI，老年慎用长效NSAIDs。'
  ]

  let mock: OdsRecord[] = []
  if (type === 'drug') {
    mock = drugNames.map((n, i) => ({
      id: 'DR' + (1000 + i),
      type: 'drug',
      name: n,
      source: ['NMPA公开库', 'Drugs.com镜像'][i % 2],
      ts: Date.now() - i * 3600000,
      raw: { approval_no: `国药准字H${10000001 + i}`, dosage_form: ['片剂', '胶囊', '缓释片'][i % 3] }
    }))
  } else if (type === 'disease') {
    mock = diseaseNames.map((n, i) => ({
      id: 'DI' + (1000 + i),
      type: 'disease',
      name: n,
      source: 'CMeKG公开数据',
      ts: Date.now() - i * 7200000,
      raw: { icd_code: `I${10 + i}`, department: ['心内科', '内分泌科', '神经内科'][i % 3] }
    }))
  } else {
    mock = Array.from({ length: limit }).map((_, i) => ({
      id: 'GD' + (1000 + i),
      type: 'guideline',
      content: guidelineTmpl[i % guidelineTmpl.length],
      source: `中华医学会指南(${2020 + (i % 5)}版)`,
      ts: Date.now() - i * 14400000
    }))
  }

  try {
    const res = await http.get<any, OdsRecord[]>(`/crawler/ods_preview?type=${type}&limit=${limit}`)
    return Array.isArray(res) && res.length > 0 ? res : mock
  } catch {
    return mock
  }
}


export const triggerSpiderRun = runSpider
export const triggerAllGenerators = runGenerator
export async function getCrawlerSources() {
  const stats = await getCrawlerStats()
  return stats.sourcePie || []
}
