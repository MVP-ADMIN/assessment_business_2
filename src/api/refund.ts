import request from '@/utils/request'
import type { RefundRecord } from '@/types/refund'

export const refundApi = {
  // 获取返款列表
  list: (params?: any) => request.get<RefundRecord[]>('/api/refunds', { params }),
  
  // 创建返款记录
  create: (data: Partial<RefundRecord>) => 
    request.post<RefundRecord>('/api/refunds', data),
  
  // 获取返款详情
  detail: (id: number) => request.get<RefundRecord>(`/api/refunds/${id}`),
  
  // 更新返款记录
  update: (id: number, data: Partial<RefundRecord>) => 
    request.put<RefundRecord>(`/api/refunds/${id}`, data),
  
  // 删除返款记录
  delete: (id: number) => request.delete(`/api/refunds/${id}`),
  
  // 获取返款统计数据
  stats: () => request.get('/api/refunds/stats'),
  
  // 导出返款数据
  export: (params?: any) => 
    request.get('/api/refunds/export', { params, responseType: 'blob' })
} 