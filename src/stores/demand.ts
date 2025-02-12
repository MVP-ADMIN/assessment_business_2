import { defineStore } from 'pinia'
import type { Demand } from '../types/demand'
import { getDemands, getAllOptions } from '../api/demand'

export const useDemandStore = defineStore('demand', {
  state: () => ({
    demands: [] as Demand[],
    options: {
      status: [],
      models: [],
      types: [],
      platforms: [],
      countries: [],
      brands: [],
      stores: [],
      accounts: [],
      methods: [],
      adEntryOptions: [],
      variantOptions: []
    },
    loading: false
  }),
  
  actions: {
    async fetchDemands() {
      this.loading = true
      try {
        const { data } = await getDemands()
        this.demands = data
      } finally {
        this.loading = false
      }
    },
    
    async loadOptions() {
      try {
        const { data } = await getAllOptions()
        this.options = data
      } catch (error) {
        console.error('Failed to load options:', error)
      }
    }
  }
}) 