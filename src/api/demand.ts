import request from '@/utils/request'
import type { Demand } from '@/types/demand'
import { ElMessage } from 'element-plus'
import type { DemandDetail } from '@/types/detail'

// 定义选项接口返回类型
interface OptionsResponse {
  models: Array<{ model_id: number; model_name: string }>
  types: Array<{ type_id: number; type_name: string }>
  platforms: Array<{ platform_id: number; platform_name: string }>
  countries: Array<{ country_id: number; country_name: string }>
  brands: Array<{ brand_id: number; brand_name: string }>
  stores: Array<{ store_id: number; store_name: string }>
  accounts: Array<{ account_id: number; account_name: string }>
  methods: Array<{ method_id: number; method_name: string }>
  adEntryOptions: Array<{ option_id: number; option_name: string }>
  variantOptions: Array<{ option_id: number; option_name: string }>
}

export const getDemands = () => {
  return request.get<Demand[]>('/api/demands')
}

export const getAllOptions = () => {
  return request.get<OptionsResponse>('/api/options')
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
  create: (data: Partial<Demand>) => 
    request.post<Demand>('/api/demands', {
      ...data,
      // 确保这些字段有值
      model_id: data.model_id,
      type_id: data.type_id,
      platform_id: data.platform_id,
      country_id: data.country_id,
      brand_id: data.brand_id,
      store_id: data.store_id,
      account_id: data.account_id,
      method_id: data.method_id,
      // 设置默认值
      status_id: data.status_id || 1,
      ordered_quantity: data.ordered_quantity || 0,
      unordered_quantity: data.unordered_quantity || 0,
      reviewed_quantity: data.reviewed_quantity || 0,
      unreviewed_quantity: data.unreviewed_quantity || 0
    }),
  
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