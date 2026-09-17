export interface SseTraceEvent {
  type: 'trace'
  hop: number
  node: string
  nodeType: 'drug' | 'disease' | 'ingredient' | 'symptom'
  relation: string
  target?: string
}

export interface SseTokenEvent {
  type: 'token'
  content: string
}

export interface SseDoneEvent {
  type: 'done'
  totalTokens: number
  totalHops: number
  cacheHit: boolean
  durationMs: number
}

export type SseEvent = SseTraceEvent | SseTokenEvent | SseDoneEvent

export interface SseCallbacks {
  onTrace?: (event: SseTraceEvent) => void
  onToken?: (event: SseTokenEvent) => void
  onDone?: (event: SseDoneEvent) => void
  onError?: (error: any) => void
}

export function createSseConnection(
  sessionId: string,
  query: string,
  callbacks: SseCallbacks,
  useMock: boolean = true
): EventSource | null {
  if (useMock) {
    simulateSseStream(query, callbacks)
    return null
  }

  const token = localStorage.getItem('medgraph_token') || ''
  const url = `/sse/chat/stream?sessionId=${encodeURIComponent(sessionId)}&query=${encodeURIComponent(query)}&token=${encodeURIComponent(token)}`

  try {
    const es = new EventSource(url, { withCredentials: true })

    es.addEventListener('trace', (e: MessageEvent) => {
      try { callbacks.onTrace?.(JSON.parse(e.data)) } catch {}
    })
    es.addEventListener('token', (e: MessageEvent) => {
      callbacks.onToken?.({ type: 'token', content: e.data })
    })
    es.addEventListener('done', (e: MessageEvent) => {
      try { callbacks.onDone?.(JSON.parse(e.data)) } catch {}
      es.close()
    })
    es.addEventListener('error', (e) => {
      callbacks.onError?.(e)
      es.close()
    })

    return es
  } catch (e) {
    callbacks.onError?.(e)
    simulateSseStream(query, callbacks)
    return null
  }
}

export function simulateSseStream(query: string, callbacks: SseCallbacks) {
  const traces: SseTraceEvent[] = [
    { type: 'trace', hop: 1, node: query.replace(/[的吗？?呢]/g, '').slice(0, 4) || '高血压', nodeType: 'disease', relation: 'TREATS', target: '卡托普利' },
    { type: 'trace', hop: 2, node: '卡托普利', nodeType: 'drug', relation: 'CONTAINS', target: '卡托普利成分' },
    { type: 'trace', hop: 3, node: '卡托普利', nodeType: 'drug', relation: 'CONTRAINDICATED_WITH', target: '双侧肾动脉狭窄' },
  ]

  traces.forEach((t, i) => {
    setTimeout(() => callbacks.onTrace?.(t), 200 + i * 300)
  })

  const mockAnswer = `关于「${query || '您的问题'}」，根据医疗知识图谱分析如下：

【诊断与用药建议】
1. 首先建议明确诊断分型，完善相关检查（血压监测、血脂、肝肾功能、心电图等）。
2. 一线用药推荐：
   • ACEI类（如卡托普利 25mg tid 或 依那普利 10mg qd）
   • CCB类（如硝苯地平缓释片 30mg qd）
   • 必要时联合β受体阻滞剂（美托洛尔）或利尿剂（氢氯噻嗪）
3. 禁忌提示：ACEI类禁用于双侧肾动脉狭窄、妊娠及高钾血症患者；用药前需评估肾功能。

【相互作用警戒】
• 华法林与阿司匹林联用出血风险升高2~3倍，需监测INR目标2.0~3.0
• 喹诺酮类抗菌药与茶碱联用可致茶碱血药浓度升高，需减量并监测
• 他汀类与红霉素/奥美拉唑等CYP3A4抑制剂联用横纹肌溶解风险增加

【随访与监测】
• 起始治疗每2~4周复诊评估疗效与不良反应
• 定期监测血压、心率、肝肾功能、电解质（血钾）
• 生活方式干预为基础：低盐饮食、规律运动、戒烟限酒、控制体重

以上建议仅供参考，具体诊疗请遵医嘱并结合患者实际情况。`

  const chars = mockAnswer.split('')
  let idx = 0
  const tokenInterval = setInterval(() => {
    if (idx >= chars.length) {
      clearInterval(tokenInterval)
      setTimeout(() => {
        callbacks.onDone?.({
          type: 'done',
          totalTokens: chars.length,
          totalHops: traces.length,
          cacheHit: Math.random() > 0.6,
          durationMs: 800 + Math.floor(Math.random() * 1500)
        })
      }, 200)
      return
    }
    const batchSize = Math.min(2 + Math.floor(Math.random() * 4), chars.length - idx)
    const batch = chars.slice(idx, idx + batchSize).join('')
    idx += batchSize
    callbacks.onToken?.({ type: 'token', content: batch })
  }, 15)
}


export function sseStreamChat(
  query: string,
  sessionId: string,
  callbacks: {
    onTrace?: (trace: any) => void
    onToken?: (token: string) => void
    onDone?: (done?: any) => void
    onError?: (err?: any) => void
  }
) {
  createSseConnection(
    sessionId,
    query,
    {
      onTrace: (t) => callbacks.onTrace?.(t),
      onToken: (tok) => callbacks.onToken?.(tok.content),
      onDone: (d) => callbacks.onDone?.(d),
      onError: (e) => callbacks.onError?.(e)
    },
    true
  )
}
