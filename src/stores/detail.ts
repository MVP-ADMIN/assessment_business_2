import { defineStore } from 'pinia'
import { getDemandDetails } from '../api/detail'
import type { DemandDetail } from '../types/detail'

export const useDetailStore = defineStore('detail', {
  state: () => ({
    details: [] as DemandDetail[],
    loading: false
  }),
  
  getters: {
    totalAmount: (state) => {
      return state.details.reduce((sum, detail) => sum + detail.order_amount, 0)
    },
    
    statusCounts: (state) => {
      const counts = { 1: 0, 2: 0, 3: 0 }
      state.details.forEach(detail => {
        if (detail.status in counts) {
          counts[detail.status as keyof typeof counts] += 1
        }
      })
      return counts
    },
    
    completionRate: (state) => {
      if (!state.details.length) return 0
      const completed = state.details.filter(d => d.status === 3).length
      return (completed / state.details.length * 100).toFixed(1)
    }
  },
  
  actions: {
    async loadDetails(demandId: number) {
      this.loading = true
      try {
        const { data } = await getDemandDetails(demandId)
        this.details = data
      } finally {
        this.loading = false
      }
    },
    
    addDetail(detail: DemandDetail) {
      this.details.unshift(detail)
    },
    
    updateDetail(detailId: number, updatedDetail: Partial<DemandDetail>) {
      const index = this.details.findIndex(d => d.detail_id === detailId)
      if (index !== -1) {
        this.details[index] = { ...this.details[index], ...updatedDetail }
      }
    },
    
    removeDetail(detailId: number) {
      const index = this.details.findIndex(d => d.detail_id === detailId)
      if (index !== -1) {
        this.details.splice(index, 1)
      }
    }
  }
}) 