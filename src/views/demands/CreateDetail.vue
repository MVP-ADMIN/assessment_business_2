<template>
  <div class="create-detail">
    <div class="header">
      <h2>新增测评明细</h2>
      <el-button @click="router.back()">返回</el-button>
    </div>
    
    <demand-detail-form
      :demand-id="Number(route.params.demandId)"
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import DemandDetailForm from '../../components/DemandDetailForm.vue'
import type { DemandDetail } from '../../types/detail'
import axios from 'axios'
import { computed } from 'vue'

const router = useRouter()
const route = useRoute()
const demandId = computed(() => route.params.id)

const handleSubmit = async (formData: Partial<DemandDetail>) => {
  try {
    // 格式化日期时间
    if (formData.order_time) {
      formData.order_time = formatDateTime(formData.order_time)
    }
    if (formData.review_time) {
      formData.review_time = formatDateTime(formData.review_time)
    }

    const { data: response } = await axios.post('/api/demand-details', {
      ...formData,
      demand_id: parseInt(demandId.value)
    })
    
    if (response.code === 0) {
      ElMessage.success('创建成功')
      router.push({
        name: 'DemandDetail',
        params: { id: demandId.value }
      })
    } else {
      ElMessage.error(response.message || '创建失败')
    }
  } catch (error) {
    console.error('Failed to create detail:', error)
    ElMessage.error('创建失败')
  }
}

// 格式化日期时间为MySQL格式
const formatDateTime = (date: Date | string) => {
  const d = new Date(date)
  return d.toISOString().slice(0, 19).replace('T', ' ')
}
</script>

<style scoped>
.create-detail {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style> 