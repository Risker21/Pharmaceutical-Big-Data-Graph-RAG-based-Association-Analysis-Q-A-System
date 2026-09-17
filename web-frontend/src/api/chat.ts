import http from './http'

export interface ChatSession {
  id: string
  title: string
  createdAt: number
  updatedAt: number
  messageCount: number
}

export interface ChatMessage {
  id: string
  sessionId: string
  role: 'user' | 'assistant'
  content: string
  createdAt: number
  durationMs?: number
  tokensUsed?: number
  cacheHit?: boolean
  retrievalTraces?: any[]
}

export async function getSessions(): Promise<ChatSession[]> {
  const mock: ChatSession[] = Array.from({ length: 8 }).map((_, i) => ({
    id: 'S' + (1000 + i),
    title: ['高血压用药咨询', '糖尿病联合方案', '冠心病二级预防', '华法林出血风险', '药物相互作用查询', '抗生素使用规范', '他汀类肌病排查', '肾功能不全用药调整'][i],
    createdAt: Date.now() - i * 86400000 * 2,
    updatedAt: Date.now() - i * 86400000 * 2 + 3600000,
    messageCount: 3 + (i % 5)
  }))
  try {
    const res = await http.get<any, ChatSession[]>('/chat/sessions')
    return Array.isArray(res) && res.length > 0 ? res : mock
  } catch {
    return mock
  }
}

export async function getSessionMessages(sessionId: string): Promise<ChatMessage[]> {
  const mock: ChatMessage[] = [
    {
      id: 'M1',
      sessionId,
      role: 'user',
      content: '高血压合并糖尿病，ACEI和二甲双胍能一起用吗？',
      createdAt: Date.now() - 600000
    },
    {
      id: 'M2',
      sessionId,
      role: 'assistant',
      content: '可以联用，且为高血压合并糖尿病的优选组合方案之一。ACEI（如卡托普利、依那普利）具有肾保护作用，可减少糖尿病肾病进展；二甲双胍为2型糖尿病一线用药。联用需注意：①监测肾功能（eGFR<45时二甲双胍需调整）；②警惕高钾血症风险（ACEI保钾+糖尿病肾损易致高钾）；③低血糖症状可能被ACEI干咳掩盖需留意。建议从小剂量起始，每2周复查电解质。',
      createdAt: Date.now() - 598000,
      durationMs: 2150,
      tokensUsed: 412,
      cacheHit: false,
      retrievalTraces: [
        { hop: 1, node: '高血压', type: 'disease', rel: 'TREATS', target: '卡托普利' },
        { hop: 2, node: '糖尿病', type: 'disease', rel: 'TREATS', target: '二甲双胍' },
        { hop: 3, node: '卡托普利', type: 'drug', rel: 'INTERACT', target: '二甲双胍' }
      ]
    },
    {
      id: 'M3',
      sessionId,
      role: 'user',
      content: '需要加用他汀吗？',
      createdAt: Date.now() - 300000
    },
    {
      id: 'M4',
      sessionId,
      role: 'assistant',
      content: '建议评估ASCVD风险分层后决定：①若合并冠心病/脑梗/外周动脉病，属极高危，必须加用他汀（目标LDL-C<1.4mmol/L）；②若仅高血压+糖尿病无靶器官损害，属高危，推荐加用中等强度他汀（如辛伐他汀20~40mg或阿托伐他汀10~20mg qn，目标LDL-C<1.8mmol/L）；③用药前及3个月后复查ALT/AST及CK，若肌痛乏力及时就诊。他汀与ACEI/二甲双胍无严重相互作用，但与红霉素/奥美拉唑等同服需减量。',
      createdAt: Date.now() - 298000,
      durationMs: 2890,
      tokensUsed: 578,
      cacheHit: false,
      retrievalTraces: [
        { hop: 1, node: '高血压', type: 'disease', rel: 'COMPLICATED_WITH', target: '高脂血症' },
        { hop: 2, node: '高脂血症', type: 'disease', rel: 'TREATS', target: '辛伐他汀' },
        { hop: 3, node: '辛伐他汀', type: 'drug', rel: 'CYP3A4_SUBSTRATE' }
      ]
    }
  ]
  try {
    const res = await http.get<any, ChatMessage[]>('/chat/sessions/' + sessionId + '/messages')
    return Array.isArray(res) && res.length > 0 ? res : mock
  } catch {
    return mock
  }
}

export async function createSession(title: string): Promise<ChatSession> {
  const mock: ChatSession = {
    id: 'S' + Date.now(),
    title: title || '新会话',
    createdAt: Date.now(),
    updatedAt: Date.now(),
    messageCount: 0
  }
  try {
    const res = await http.post<any, ChatSession>('/chat/sessions', { title })
    return res && res.id ? res : mock
  } catch {
    return mock
  }
}

export async function deleteSession(sessionId: string): Promise<void> {
  try {
    await http.delete('/chat/sessions/' + sessionId)
  } catch {}
}

export async function sendMessage(sessionId: string, content: string): Promise<ChatMessage> {
  const mock: ChatMessage = {
    id: 'M' + Date.now(),
    sessionId,
    role: 'user',
    content,
    createdAt: Date.now()
  }
  try {
    const res = await http.post<any, ChatMessage>('/chat/sessions/' + sessionId + '/messages', { content })
    return res && res.id ? res : mock
  } catch {
    return mock
  }
}
