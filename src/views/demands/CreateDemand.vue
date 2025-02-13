<template>
  <div class="create-demand">
    <div class="header">
      <h2>创建需求</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>
    
    <DemandForm
      ref="formRef"
      v-model="formData"
    />
    
    <div class="form-actions">
      <el-button type="primary" @click="handleSubmit">保存</el-button>
      <el-button @click="$router.back()">取消</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import DemandForm from '@/components/DemandForm.vue'
import { demandApi } from '@/api/demand'
import { DemandStatus } from '@/types/demand'

const router = useRouter()
const formRef = ref()

const formData = ref({
  marketing_number: '',
  dingtalk_number: '',
  asin: '',
  assessment_quantity: 0,
  text_review_quantity: 0,
  image_review_quantity: 0,
  video_review_quantity: 0,
  product_price: null,
  search_keyword: '',
  hyperlink: '',
  other_notes: '',
  status_id: DemandStatus.PENDING,
  model_id: undefined,       // 必填
  type_id: undefined,       // 必填
  platform_id: undefined,   // 必填
  country_id: undefined,    // 必填
  brand_id: undefined,      // 必填
  store_id: undefined,      // 必填
  account_id: undefined,    // 必填
  method_id: undefined,     // 必填
  ad_entry_option_id: undefined,
  variant_option_id: undefined,
  ordered_quantity: 0,
  unordered_quantity: 0,
  reviewed_quantity: 0,
  unreviewed_quantity: 0,
  registration_date: null,
  first_order_date: null
})

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    // 确保所有必填字段都有值
    const requiredFields = [
      'model_id', 'type_id', 'platform_id', 'country_id',
      'brand_id', 'store_id', 'account_id', 'method_id',
      'ad_entry_option_id', 'variant_option_id'
    ]
    
    const missingFields = requiredFields.filter(field => !formData.value[field])
    if (missingFields.length > 0) {
      ElMessage.error(`请填写必填字段: ${missingFields.join(', ')}`)
      return
    }
    
    // 提交数据
    await demandApi.create(formData.value)
    ElMessage.success('创建成功')
    router.push('/demands')
  } catch (error) {
    console.error('Failed to create demand:', error)
    ElMessage.error('创建失败')
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