import http from './http'

export interface DashboardStats {
  totalNodes: number
  totalEdges: number
  totalQuestions: number
  totalDrugs: number
  totalDiseases: number
  avgResponseMs: number
  cacheHitRate: number
  todaySessions: number
  topKpis: {
    label: string
    value: number
    unit: string
    trend: number
    color: string
  }[]
  departmentDistribution: { name: string; value: number }[]
  sevenDayTrend: {
    date: string
    sessions: number
    questions: number
    avgMs: number
  }[]
  radarData: {
    name: string
    value: number[]
  }[]
  topContraindications: {
    pair: string[]
    level: 'High' | 'Medium' | 'Low'
    count: number
    risk: string
  }[]
  healthStatus: {
    crawler: 'green' | 'yellow' | 'red'
    etl: 'green' | 'yellow' | 'red'
    graph: 'green' | 'yellow' | 'red'
    ai: 'green' | 'yellow' | 'red'
    gateway: 'green' | 'yellow' | 'red'
  }
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const now = new Date()
  const sevenDay = Array.from({ length: 7 }).map((_, i) => {
    const d = new Date(now.getTime() - (6 - i) * 86400000)
    return `${d.getMonth() + 1}-${d.getDate()}`
  })

  const mock: DashboardStats = {
    totalNodes: 432158,
    totalEdges: 1256890,
    totalQuestions: 18956,
    totalDrugs: 2156,
    totalDiseases: 892,
    avgResponseMs: 1842,
    cacheHitRate: 0.623,
    todaySessions: 248,
    topKpis: [
      { label: '今日会话', value: 248, unit: '次', trend: 12.5, color: '#1677ff' },
      { label: '平均响应', value: 1842, unit: 'ms', trend: -8.3, color: '#52c41a' },
      { label: '缓存命中', value: 62.3, unit: '%', trend: 5.7, color: '#faad14' },
      { label: '图谱节点', value: 432158, unit: '个', trend: 2.1, color: '#722ed1' }
    ],
    departmentDistribution: [
      { name: '心内科', value: 4820 },
      { name: '内分泌科', value: 3956 },
      { name: '呼吸内科', value: 2812 },
      { name: '消化内科', value: 2234 },
      { name: '神经内科', value: 1987 },
      { name: '骨科/风湿', value: 1543 },
      { name: '全科', value: 1604 }
    ],
    sevenDayTrend: sevenDay.map((date, i) => ({
      date,
      sessions: 180 + Math.floor(Math.random() * 100) + i * 8,
      questions: 320 + Math.floor(Math.random() * 200) + i * 12,
      avgMs: 1500 + Math.floor(Math.random() * 800)
    })),
    radarData: [
      { name: '心内科', value: [92, 88, 76, 81, 95] },
      { name: '内分泌科', value: [85, 91, 82, 78, 88] },
      { name: '呼吸内科', value: [72, 68, 90, 85, 75] }
    ],
    topContraindications: [
      { pair: ['华法林', '阿司匹林'], level: 'High', count: 1284, risk: '出血风险升高2-3倍' },
      { pair: ['左氧氟沙星', '茶碱'], level: 'High', count: 956, risk: '茶碱血药浓度升高致心律失常' },
      { pair: ['布洛芬', '华法林'], level: 'High', count: 872, risk: '上消化道出血风险RR≈3.2' },
      { pair: ['对乙酰氨基酚', '复方感冒药'], level: 'High', count: 641, risk: '重复用药致肝损伤' },
      { pair: ['ACEI', '螺内酯'], level: 'Medium', count: 523, risk: '高钾血症风险' },
      { pair: ['辛伐他汀', '红霉素'], level: 'Medium', count: 389, risk: '横纹肌溶解风险' }
    ],
    healthStatus: {
      crawler: 'green',
      etl: 'green',
      graph: 'green',
      ai: 'green',
      gateway: 'green'
    }
  }

  try {
    const res = await http.get<any, DashboardStats>('/dashboard/stats')
    return res && res.topKpis ? res : mock
  } catch {
    return mock
  }
}
