<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-width="120px"
    class="demand-form"
  >
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
        </div>
      </template>

      <el-form-item label="营销编号" prop="marketing_number">
        <el-input v-model="formData.marketing_number" />
      </el-form-item>

      <el-form-item label="钉钉号" prop="dingtalk_number">
        <el-input v-model="formData.dingtalk_number" />
      </el-form-item>

      <el-form-item label="ASIN" prop="asin">
        <el-input v-model="formData.asin" />
      </el-form-item>

      <el-form-item label="评估数量" prop="assessment_quantity">
        <el-input-number v-model="formData.assessment_quantity" :min="0" />
      </el-form-item>

      <el-form-item label="文字评论数" prop="text_review_quantity">
        <el-input-number v-model="formData.text_review_quantity" :min="0" />
      </el-form-item>

      <el-form-item label="图片评论数" prop="image_review_quantity">
        <el-input-number v-model="formData.image_review_quantity" :min="0" />
      </el-form-item>

      <el-form-item label="视频评论数" prop="video_review_quantity">
        <el-input-number v-model="formData.video_review_quantity" :min="0" />
      </el-form-item>

      <el-form-item label="产品价格" prop="product_price">
        <el-input-number 
          v-model="formData.product_price" 
          :precision="2"
          :step="0.01"
          :min="0"
        />
      </el-form-item>
    </el-card>

    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <span>其他信息</span>
        </div>
      </template>

      <el-form-item label="搜索关键词" prop="search_keyword">
        <el-input
          v-model="formData.search_keyword"
          type="textarea"
          :rows="2"
        />
      </el-form-item>

      <el-form-item label="链接" prop="hyperlink">
        <el-input v-model="formData.hyperlink" />
      </el-form-item>

      <el-form-item label="备注" prop="other_notes">
        <el-input
          v-model="formData.other_notes"
          type="textarea"
          :rows="3"
        />
      </el-form-item>

      <el-form-item label="状态" prop="status_id">
        <el-select v-model="formData.status_id">
          <el-option
            v-for="item in statusOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
    </el-card>

    <div class="form-actions">
      <el-button type="primary" @click="handleSubmit">保存</el-button>
      <el-button @click="$router.back()">取消</el-button>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { FormInstance } from 'element-plus'
import { DemandStatus } from '@/types/demand'

const props = defineProps<{
  initialData?: any
}>()

const emit = defineEmits<{
  submit: [data: any]
}>()

const formRef = ref<FormInstance>()
const formData = ref({
  marketing_number: '',
  dingtalk_number: '',
  asin: '',
  assessment_quantity: 0,
  text_review_quantity: 0,
  image_review_quantity: 0,
  video_review_quantity: 0,
  product_price: 0,
  search_keyword: '',
  hyperlink: '',
  other_notes: '',
  status_id: DemandStatus.PENDING
})

const statusOptions = [
  { value: DemandStatus.PENDING, label: '待处理' },
  { value: DemandStatus.PROCESSING, label: '进行中' },
  { value: DemandStatus.PAUSED, label: '已暂停' },
  { value: DemandStatus.COMPLETED, label: '已完成' },
  { value: DemandStatus.CANCELLED, label: '已取消' }
]

const rules = {
  marketing_number: [
    { required: true, message: '请输入营销编号', trigger: 'blur' }
  ],
  dingtalk_number: [
    { required: true, message: '请输入钉钉号', trigger: 'blur' }
  ],
  asin: [
    { required: true, message: '请输入ASIN', trigger: 'blur' }
  ],
  assessment_quantity: [
    { required: true, message: '请输入评估数量', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    emit('submit', formData.value)
  } catch (error) {
    // 表单验证失败
  }
}

onMounted(() => {
  if (props.initialData) {
    formData.value = {
      ...formData.value,
      ...props.initialData
    }
  }
})
</script>

<style scoped>
.demand-form {
  max-width: 1200px;
  margin: 0 auto;
}

.form-card {
  margin-bottom: 20px;
}

.form-actions {
  text-align: center;
  margin-top: 20px;
}
</style> 