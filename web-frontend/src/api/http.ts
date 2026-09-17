import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const service: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('medgraph_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    if (res && res.code !== undefined && res.code !== 0 && res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || 'Error'))
    }
    return res.data !== undefined ? res.data : res
  },
  async (error) => {
    const status = error.response?.status
    if (status === 401) {
      localStorage.removeItem('medgraph_token')
      localStorage.removeItem('medgraph_user')
      ElMessage.warning('登录已过期，请重新登录')
      router.push('/login')
    }
    return Promise.resolve(error.config?._mockFallback ?? {})
  }
)

export const useMock = <T>(fallback: T): T => fallback

export default service
