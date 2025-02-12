<template>
  <div class="create-demand">
    <h2>创建需求</h2>
    <demand-form @submit="handleSubmit" />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import DemandForm from '../../components/DemandForm.vue'

const router = useRouter()

const handleSubmit = async (formData) => {
  try {
    await axios.post('/api/demands', formData)
    ElMessage.success('创建成功')
    router.push('/demands')
  } catch (error) {
    ElMessage.error('创建失败')
  }
}
</script>

<style scoped>
.create-demand {
  padding: 20px;
}
</style> 