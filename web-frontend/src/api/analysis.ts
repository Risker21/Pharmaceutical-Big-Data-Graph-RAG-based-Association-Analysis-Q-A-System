import http from './http'

export interface ChatAnalysis {
  total_sessions: number
  total_messages: number
  total_tokens_used: number
  avg_response_ms: number
  avg_tokens_per_answer: number
  cache_hit_rate: number
  rate_limit_blocked: number
  avg_hop_count_per_trace: number
  avg_retrieval_chunks: number
  daily_trend: { date: string; sessions: number; messages: number; tokens: number }[]
  intent_distribution: { intent: string; count: number; color: string }[]
  top_asked_questions: { query: string; count: number }[]
  qps_last_5min: {
    time: string[]
    passed: number[]
    blocked: number[]
  }
  recent_qa: {
    id: string
    ts: number
    user: string
    query: string
    intent: string
    response_ms: number
    tokens: number
    cache_hit: boolean
    retrievalTraces?: any[]
  }[]
}

export async function getChatAnalysis(range: string = '7d'): Promise<ChatAnalysis> {
  const now = new Date()
  const daily = Array.from({ length: 7 }).map((_, i) => {
    const d = new Date(now.getTime() - (6 - i) * 86400000)
    return `${d.getMonth() + 1}-${d.getDate()}`
  })
  const qpsTimes = Array.from({ length: 300 }).map((_, i) => {
    const d = new Date(Date.now() - (299 - i) * 1000)
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
  })

  const queries = [
    '高血压和糖尿病合并用药', '华法林和阿司匹林能一起吃吗', '他汀类副作用有哪些',
    '二甲双胍饭前还是饭后吃', 'ACEI和ARB区别', '感冒发烧用什么药',
    '冠心病二级预防用药方案', '房颤抗凝选华法林还是NOAC', '痛风急性期用药',
    '幽门螺杆菌根除方案', '慢性肾病用药调整', '老年高血压首选药',
    '青霉素过敏头孢能用吗', '喹诺酮类禁忌症', '磺脲类降糖药有哪些',
    '倍他乐克停药注意事项', '呋塞米和螺内酯联用', '奥美拉唑长期服用风险'
  ]
  const intents = ['用药咨询', '相互作用查询', '禁忌排查', '给药方案建议', '不良反应解读', '诊断辅助', '随访管理', '检查解读']
  const users = ['admin', 'doctor_wang', 'doctor_li', 'doctor_zhang', 'intern_chen', 'pharmacist_zhao']

  const mock: ChatAnalysis = {
    total_sessions: 1892,
    total_messages: 7245,
    total_tokens_used: 3284920,
    avg_response_ms: 1842,
    avg_tokens_per_answer: 458,
    cache_hit_rate: 0.623,
    rate_limit_blocked: 37,
    avg_hop_count_per_trace: 2.73,
    avg_retrieval_chunks: 4.21,
    daily_trend: daily.map(date => ({
      date,
      sessions: 180 + Math.floor(Math.random() * 120),
      messages: 600 + Math.floor(Math.random() * 400),
      tokens: 250000 + Math.floor(Math.random() * 150000)
    })),
    intent_distribution: [
      { intent: '用药咨询', count: 2341, color: '#1677ff' },
      { intent: '相互作用查询', count: 1523, color: '#52c41a' },
      { intent: '禁忌排查', count: 1187, color: '#ff4d4f' },
      { intent: '给药方案建议', count: 956, color: '#faad14' },
      { intent: '不良反应解读', count: 742, color: '#722ed1' },
      { intent: '诊断辅助', count: 312, color: '#13c2c2' },
      { intent: '其他', count: 184, color: '#909399' }
    ],
    top_asked_questions: queries.map((q, i) => ({
      query: q,
      count: 500 - i * 20 + Math.floor(Math.random() * 50)
    })),
    qps_last_5min: {
      time: qpsTimes,
      passed: qpsTimes.map((_, i) => 3 + Math.floor(Math.random() * 8) + Math.floor(Math.sin(i / 20) * 3)),
      blocked: qpsTimes.map(() => Math.random() > 0.9 ? Math.floor(Math.random() * 3) : 0)
    },
    recent_qa: Array.from({ length: 50 }).map((_, i) => ({
      id: 'QA' + (100000 + i),
      ts: Date.now() - i * 180000 - Math.random() * 60000,
      user: users[i % users.length],
      query: queries[i % queries.length],
      intent: intents[i % intents.length],
      response_ms: 800 + Math.floor(Math.random() * 3500),
      tokens: 200 + Math.floor(Math.random() * 800),
      cache_hit: Math.random() > 0.6,
      retrievalTraces: [
        { hop: 1, node: '高血压', type: 'disease', rel: 'TREATS', target: '卡托普利' },
        { hop: 2, node: '卡托普利', type: 'drug', rel: 'SAME_CLASS', target: '依那普利' }
      ]
    }))
  }

  try {
    const res = await http.get<any, ChatAnalysis>(`/analysis/chat-stats?range=${range}`)
    return res && res.total_sessions ? res : mock
  } catch {
    return mock
  }
}

export async function getChatFull(from?: string, to?: string): Promise<ChatAnalysis> {
  return getChatAnalysis('custom')
}


export const getChatFullAnalysis = getChatAnalysis
