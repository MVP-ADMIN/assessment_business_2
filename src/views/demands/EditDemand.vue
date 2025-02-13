<template>
  <div class="edit-demand">
    <div class="header">
      <h2>编辑需求</h2>
    </div>
    
    <div v-loading="loading">
      <DemandForm
        v-if="formData"
        :initial-data="formData"
        @submit="handleSubmit"
      />
      <div v-else class="loading-placeholder">
        <el-empty description="加载中..." />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import DemandForm from '@/components/DemandForm.vue'
import { demandApi } from '@/api/demand'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const formData = ref<any>(null)

const loadDemand = async () => {
  try {
    loading.value = true
    const data = await demandApi.detail(Number(route.params.id))
    formData.value = data
  } catch (error) {
    console.error('Failed to load demand:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async (data: any) => {
  try {
    loading.value = true
    await demandApi.update(Number(route.params.id), data)
    ElMessage.success('保存成功')
    router.push('/demands')
  } catch (error) {
    console.error('Failed to update demand:', error)
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDemand()
})
</script>

<style scoped>
.edit-demand {
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.loading-placeholder {
  padding: 40px;
  text-align: center;
}
</style> 