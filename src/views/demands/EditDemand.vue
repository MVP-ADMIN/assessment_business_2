<template>
  <div class="edit-demand">
    <div class="header">
      <h2>编辑需求</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>
    
    <el-card v-loading="loading">
      <DemandForm
        v-if="formData"
        ref="formRef"
        v-model="formData"
        :initial-data="formData"
      />
      <div v-else class="loading-placeholder">
        <el-empty description="加载中..." />
      </div>

      <div class="form-actions">
        <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import DemandForm from '@/components/DemandForm.vue'
import { demandApi } from '@/api/demand'

const route = useRoute()
const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const formData = ref<any>(null)

// 加载需求数据
const loadDemand = async () => {
  try {
    loading.value = true
    const id = Number(route.params.id)
    const response = await demandApi.detail(id)
    
    if (response.code === 0 && response.data) {
      formData.value = response.data
    } else {
      ElMessage.error('获取需求详情失败')
    }
  } catch (error) {
    console.error('Failed to load demand:', error)
    ElMessage.error('获取需求详情失败')
  } finally {
    loading.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    const id = Number(route.params.id)
    
    const response = await demandApi.update(id, formData.value)
    if (response.code === 0) {
      ElMessage.success('保存成功')
      router.push('/demands')
    } else {
      ElMessage.error('保存失败')
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.form-actions {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.form-actions .el-button {
  min-width: 120px;
  margin: 0 10px;
}

.loading-placeholder {
  padding: 40px;
  text-align: center;
}
</style> 