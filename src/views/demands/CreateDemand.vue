<template>
  <div class="create-demand">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <h2>创建需求</h2>
        </div>
      </template>

      <demand-form 
        ref="formRef"
        :loading="loading"
        @submit="handleSubmit"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import DemandForm from '@/components/DemandForm.vue'
import { demandApi } from '@/api/demand'

const router = useRouter()
const loading = ref(false)
const formRef = ref()

const handleSubmit = async (formData: any) => {
  try {
    loading.value = true
    await demandApi.create(formData)
    ElMessage.success('创建成功')
    router.push('/demands')
  } catch (error) {
    console.error('Failed to create demand:', error)
    ElMessage.error('创建失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.create-demand {
  padding: 20px;
}

.form-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 