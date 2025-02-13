<template>
  <div class="edit-detail">
    <div class="header">
      <h2>编辑测评明细</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>
    
    <el-card v-loading="loading">
      <DemandDetailForm
        ref="formRef"
        v-model="formData"
      />
      
      <div class="form-actions">
        <el-button type="primary" @click="handleSubmit">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import DemandDetailForm from '@/components/DemandDetailForm.vue'
import { demandApi } from '@/api/demand'

const route = useRoute()
const router = useRouter()
const formRef = ref()
const loading = ref(false)
const formData = ref({})

// 加载明细数据
const loadDetail = async () => {
  try {
    loading.value = true
    const detailId = Number(route.params.detailId)
    const response = await demandApi.getDetailById(detailId)
    formData.value = response
  } catch (error) {
    console.error('Failed to load detail:', error)
    ElMessage.error('加载明细数据失败')
  } finally {
    loading.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    const detailId = Number(route.params.detailId)
    await demandApi.updateDetail(detailId, formData.value)
    ElMessage.success('保存成功')
    router.back()
  } catch (error) {
    console.error('Failed to update detail:', error)
    ElMessage.error('保存失败')
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

.form-actions {
  text-align: center;
  margin-top: 20px;
}
</style> 