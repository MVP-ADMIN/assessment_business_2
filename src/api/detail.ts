import request from '../utils/request'
import type { DemandDetail, DemandDetailForm } from '../types/detail'

export const createDemandDetail = (data: DemandDetailForm) => {
  return request.post<DemandDetail>('/api/demand-details', data)
}

export const updateDemandDetail = (id: number, data: Partial<DemandDetailForm>) => {
  return request.put<DemandDetail>(`/api/demand-details/${id}`, data)
}

export const getDemandDetail = (id: number) => {
  return request.get<DemandDetail>(`/api/demand-details/${id}`)
}

export const getDemandDetails = (demandId: number) => {
  return request.get<DemandDetail[]>(`/api/demands/${demandId}/details`)
}

export const deleteDemandDetail = (id: number) => {
  return request.delete(`/api/demand-details/${id}`)
} 