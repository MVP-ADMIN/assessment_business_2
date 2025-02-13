import request from '@/utils/request'
import type { Demand } from '@/types/demand'
import { ElMessage } from 'element-plus'
import type { DemandDetail } from '@/types/detail'

export const getDemands = () => {
  return request.get<Demand[]>('/api/demands')
}

export const getAllOptions = () => {
  return request.get('/api/options')
}

export const createDemand = (data: Partial<Demand>) => {
  return request.post('/api/demands', data)
}

export const updateDemand = (id: number, data: Partial<Demand>) => {
  return request.put(`/api/demands/${id}`, data)
}

export const deleteDemand = (id: number) => {
  return request.delete(`/api/demands/${id}`)
}

export const demandApi = {
  // 获取需求列表
  list: (params?: any) => request.get<{list: Demand[], total: number}>('/api/demands', { params }),
  
  // 创建需求
  create: (data: Partial<Demand>) => request.post<Demand>('/api/demands', data),
  
  // 获取需求详情
  detail: (id: number) => request.get<Demand>(`/api/demands/${id}`),
  
  // 更新需求
  update: (id: number, data: Partial<Demand>) => 
    request.put<Demand>(`/api/demands/${id}`, data),
  
  // 删除需求
  delete: (id: number) => request.delete(`/api/demands/${id}`),
  
  // 更新需求状态
  updateStatus: (id: number, status: number) => 
    request.put<Demand>(`/api/demands/${id}/status`, { status }),
  
  // 暂停需求
  pause: (id: number) => request.put<Demand>(`/api/demands/${id}/pause`),
  
  // 恢复需求
  resume: (id: number) => request.put<Demand>(`/api/demands/${id}/resume`),
  
  // 获取需求统计数据
  stats: () => request.get('/api/demands/stats'),
  
  // 导出需求数据
  export: (params?: any) => 
    request.get('/api/demands/export', { params, responseType: 'blob' }),
  
  // 获取需求的测评明细列表
  getDetails: (demandId: number) => 
    request.get<DemandDetail[]>(`/api/demands/${demandId}/details`),
  
  // 创建测评明细
  createDetail: (data: Partial<DemandDetail>) => 
    request.post<DemandDetail>('/api/demand-details', data),
  
  // 获取测评明细详情
  getDetailById: (detailId: number) => 
    request.get<DemandDetail>(`/api/demand-details/${detailId}`),
  
  // 更新测评明细
  updateDetail: (detailId: number, data: Partial<DemandDetail>) => 
    request.put<DemandDetail>(`/api/demand-details/${detailId}`, data),
  
  // 删除测评明细
  deleteDetail: (detailId: number) => 
    request.delete(`/api/demand-details/${detailId}`),
  
  // 更新测评明细状态
  updateDetailStatus: (detailId: number, status: number) =>
    request.put<DemandDetail>(`/api/demand-details/${detailId}/status`, { status })
} 