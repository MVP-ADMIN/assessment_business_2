<template>
  <div class="edit-detail">
    <div class="header">
      <h2>编辑测评明细</h2>
      <el-button @click="router.back()">返回</el-button>
    </div>
    
    <demand-detail-form
      v-if="detail"
      :initial-data="detail"
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import DemandDetailForm from '@/components/DemandDetailForm.vue'
import type { DemandDetail } from '@/types/detail'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const detail = ref<DemandDetail | null>(null)

const loadDetail = async () => {
  try {
    const { data: response } = await axios.get(`/api/demand-details/${route.params.detailId}`)
    if (response.code === 0) {
      detail.value = response.data
    } else {
      ElMessage.error(response.message || '加载失败')
    }
  } catch (error) {
    console.error('Failed to load detail:', error)
    ElMessage.error('加载失败')
  }
}

const handleSubmit = async (formData: Partial<DemandDetail>) => {
  try {
    const processedData = { ...formData }
    
    if (processedData.order_time) {
      try {
        const orderTime = new Date(processedData.order_time)
        processedData.order_time = orderTime.toISOString().slice(0, 19).replace('T', ' ')
      } catch (e) {
        console.error('Error formatting order_time:', e)
      }
    }
    
    if (processedData.review_time) {
      try {
        const reviewTime = new Date(processedData.review_time)
        processedData.review_time = reviewTime.toISOString().slice(0, 19).replace('T', ' ')
      } catch (e) {
        console.error('Error formatting review_time:', e)
      }
    }
    
    if (Array.isArray(processedData.review_images)) {
      processedData.review_images = processedData.review_images.filter(Boolean)
    }

    console.log('Submitting data:', processedData)

    const { data: response } = await axios.put(
      `/api/demand-details/${route.params.detailId}`, 
      processedData
    )
    
    if (response.code === 0) {
      ElMessage.success('更新成功')
      const demandId = route.params.demandId
      if (demandId) {
        router.push({
          name: 'DemandDetail',
          params: { id: String(demandId) }
        })
      } else {
        const fallbackDemandId = detail.value?.demand_id
        if (fallbackDemandId) {
          router.push({
            name: 'DemandDetail',
            params: { id: String(fallbackDemandId) }
          })
        } else {
          router.push('/demands')
        }
      }
    } else {
      ElMessage.error(response.message || '更新失败')
    }
  } catch (error) {
    console.error('Failed to update detail:', error)
    ElMessage.error('更新失败')
  }
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.edit-detail {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style> 