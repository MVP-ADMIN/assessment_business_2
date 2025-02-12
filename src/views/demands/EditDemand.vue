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
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import DemandForm from '../../components/DemandForm.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const demandId = computed(() => route.params.id)
const formData = ref<any>(null)

// 加载需求数据
const loadDemand = async () => {
  if (!demandId.value) {
    ElMessage.error('需求ID不存在')
    return
  }

  try {
    loading.value = true
    const { data: response } = await axios.get(`/api/demands/${demandId.value}`)
    if (response.code === 0) {
      formData.value = response.data
    } else {
      ElMessage.error(response.message || '获取需求详情失败')
    }
  } catch (error) {
    console.error('Failed to load demand:', error)
    ElMessage.error('获取需求详情失败')
  } finally {
    loading.value = false
  }
}

// 提交表单
const handleSubmit = async (data: any) => {
  if (!demandId.value) {
    ElMessage.error('需求ID不存在')
    return
  }

  try {
    loading.value = true
    const { data: response } = await axios.put(`/api/demands/${demandId.value}`, data)
    if (response.code === 0) {
      ElMessage.success('保存成功')
      router.push('/demands')
    } else {
      ElMessage.error(response.message || '保存失败')
    }
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