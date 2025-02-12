<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="120px"
    class="detail-form"
    v-loading="loading"
  >
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="订单号" prop="order_number">
          <el-input v-model="form.order_number" placeholder="请输入订单号" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="订单金额" prop="order_amount">
          <el-input-number 
            v-model="form.order_amount"
            :precision="2"
            :step="0.01"
            :min="0"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="下单时间" prop="order_time">
          <el-date-picker
            v-model="form.order_time"
            type="datetime"
            placeholder="选择下单时间"
          />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="评论时间" prop="review_time">
          <el-date-picker
            v-model="form.review_time"
            type="datetime"
            placeholder="选择评论时间"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="订单截图" prop="order_screenshot">
      <upload-image v-model="form.order_screenshot" />
    </el-form-item>

    <el-form-item label="支付截图" prop="payment_screenshot">
      <upload-image v-model="form.payment_screenshot" />
    </el-form-item>

    <el-form-item label="评论内容" prop="review_content">
      <el-input
        v-model="form.review_content"
        type="textarea"
        rows="4"
        placeholder="请输入评论内容"
      />
    </el-form-item>

    <el-form-item label="评论图片" prop="review_images">
      <batch-image-upload v-model="form.review_images" />
    </el-form-item>

    <el-form-item label="评论视频" prop="review_video">
      <upload-video v-model="form.review_video" />
    </el-form-item>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="评论截图" prop="review_screenshot">
          <upload-image v-model="form.review_screenshot" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option label="待评论" :value="1" />
            <el-option label="已评论" :value="2" />
            <el-option label="已完成" :value="3" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        保存
      </el-button>
      <el-button @click="$router.back()">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import UploadImage from './UploadImage.vue'
import BatchImageUpload from './BatchImageUpload.vue'
import UploadVideo from './UploadVideo.vue'

const props = defineProps<{
  demandId: number
  initialData?: any
}>()

const emit = defineEmits<{
  (e: 'submit', data: any): void
}>()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = ref({
  demand_id: props.demandId,
  order_number: '',
  order_amount: 0,
  order_time: '',
  order_screenshot: '',
  payment_screenshot: '',
  review_content: '',
  review_images: [] as string[],
  review_video: '',
  review_time: '',
  review_screenshot: '',
  status: 1,
  remark: ''
})

const rules: FormRules = {
  order_number: [
    { required: true, message: '请输入订单号', trigger: 'blur' }
  ],
  order_amount: [
    { required: true, message: '请输入订单金额', trigger: 'blur' }
  ],
  order_time: [
    { required: true, message: '请选择下单时间', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    emit('submit', form.value)
  } catch (error) {
    console.error('Form validation failed:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (props.initialData) {
    form.value = {
      ...form.value,
      ...props.initialData
    }
  }
})
</script>

<style scoped>
.detail-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
</style> 