import axios from 'axios'
import type { Demand } from '../types/demand'
import { ElMessage } from 'element-plus'

// 添加响应拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    ElMessage.error(error.response?.data?.error || '请求失败')
    return Promise.reject(error)
  }
)

export const getDemands = () => {
  return axios.get<Demand[]>('/api/demands')
}

export const getAllOptions = () => {
  return axios.get('/api/options')
}

export const createDemand = (data: Partial<Demand>) => {
  return axios.post('/api/demands', data)
}

export const updateDemand = (id: number, data: Partial<Demand>) => {
  return axios.put(`/api/demands/${id}`, data)
}

export const deleteDemand = (id: number) => {
  return axios.delete(`/api/demands/${id}`)
} 