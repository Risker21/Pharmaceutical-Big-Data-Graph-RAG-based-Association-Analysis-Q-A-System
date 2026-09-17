import http from './http'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user: {
    id: number
    username: string
    nickname: string
    avatar?: string
    roles: string[]
  }
}

export async function login(req: LoginRequest): Promise<LoginResponse> {
  const mock: LoginResponse = {
    token: 'mock-jwt-token-' + Date.now(),
    user: {
      id: 1,
      username: req.username,
      nickname: req.username === 'admin' ? '系统管理员' : req.username,
      avatar: '',
      roles: ['ROLE_ADMIN', 'ROLE_USER']
    }
  }
  try {
    const res = await http.post<any, LoginResponse>('/auth/login', req)
    return res && res.token ? res : mock
  } catch {
    return mock
  }
}

export async function logout(): Promise<void> {
  try {
    await http.post('/auth/logout')
  } catch {}
}

export async function getUserInfo(): Promise<LoginResponse['user']> {
  const saved = localStorage.getItem('medgraph_user')
  if (saved) {
    try { return JSON.parse(saved) } catch {}
  }
  const mock = {
    id: 1,
    username: 'admin',
    nickname: '系统管理员',
    avatar: '',
    roles: ['ROLE_ADMIN', 'ROLE_USER']
  }
  try {
    const res = await http.get<any, LoginResponse['user']>('/auth/info')
    return res && res.id ? res : mock
  } catch {
    return mock
  }
}
