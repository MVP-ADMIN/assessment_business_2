<template>
  <div class="create-detail">
    <div class="header">
      <h2>新增测评明细</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>
    
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
      class="detail-form"
    >
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>订单信息</span>
          </div>
        </template>

        <el-form-item label="订单号" prop="order_number">
          <el-input v-model="formData.order_number" />
        </el-form-item>

        <el-form-item label="订单金额" prop="order_amount">
          <el-input-number 
            v-model="formData.order_amount"
            :precision="2"
            :step="0.01"
            :min="0"
          />
        </el-form-item>

        <el-form-item label="下单时间" prop="order_time">
          <el-date-picker
            v-model="formData.order_time"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择下单时间"
          />
        </el-form-item>

        <el-form-item label="订单截图" prop="order_screenshot">
          <UploadImage v-model="formData.order_screenshot" />
        </el-form-item>

        <el-form-item label="支付截图" prop="payment_screenshot">
          <UploadImage v-model="formData.payment_screenshot" />
        </el-form-item>
      </el-card>

      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>评价信息</span>
          </div>
        </template>

        <el-form-item label="评价时间" prop="review_time">
          <el-date-picker
            v-model="formData.review_time"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择评价时间"
          />
        </el-form-item>

        <el-form-item label="评价内容" prop="review_content">
          <el-input
            v-model="formData.review_content"
            type="textarea"
            :rows="4"
            placeholder="请输入评价内容"
          />
        </el-form-item>

        <el-form-item label="评价图片" prop="review_images">
          <UploadImage
            v-model="formData.review_images"
            :limit="5"
            multiple
          />
        </el-form-item>

        <el-form-item label="评价视频" prop="review_video">
          <UploadVideo v-model="formData.review_video" />
        </el-form-item>

        <el-form-item label="评价截图" prop="review_screenshot">
          <UploadImage v-model="formData.review_screenshot" />
        </el-form-item>
      </el-card>

      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>其他信息</span>
          </div>
        </template>

        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="formData.remark"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
      </el-card>

      <div class="form-actions">
        <el-button type="primary" @click="handleSubmit">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { demandApi } from '@/api/demand'
import { DetailStatus } from '@/types/detail'
import UploadImage from '@/components/UploadImage.vue'
import UploadVideo from '@/components/UploadVideo.vue'

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInstance>()

const formData = ref({
  demand_id: Number(route.params.demandId),
  order_number: '',
  order_amount: 0,
  order_time: '',
  review_time: '',
  review_content: '',
  review_images: [] as string[],
  review_video: '',
  payment_screenshot: '',
  order_screenshot: '',
  review_screenshot: '',
  status: DetailStatus.PENDING,
  remark: ''
})

const statusOptions = [
  { value: DetailStatus.PENDING, label: '待处理' },
  { value: DetailStatus.ORDERED, label: '已下单' },
  { value: DetailStatus.REVIEWED, label: '已评价' },
  { value: DetailStatus.CANCELLED, label: '已取消' }
]

const rules = {
  order_number: [
    { required: true, message: '请输入订单号', trigger: 'blur' }
  ],
  order_amount: [
    { required: true, message: '请输入订单金额', trigger: 'blur' }
  ],
  order_time: [
    { required: true, message: '请选择下单时间', trigger: 'change' }
  ],
  order_screenshot: [
    { required: true, message: '请上传订单截图', trigger: 'change' }
  ],
  payment_screenshot: [
    { required: true, message: '请上传支付截图', trigger: 'change' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    const submitData = {
      ...formData.value,
      review_images: formData.value.review_images || [],
      review_time: formData.value.review_time || null,
      review_video: formData.value.review_video || null,
      payment_screenshot: formData.value.payment_screenshot || null,
      order_screenshot: formData.value.order_screenshot || null,
      review_screenshot: formData.value.review_screenshot || null,
      remark: formData.value.remark || null
    }
    
    await demandApi.createDetail(submitData)
    ElMessage.success('创建成功')
    router.push(`/demands/${route.params.demandId}`)
  } catch (error) {
    console.error('Failed to create detail:', error)
    ElMessage.error('创建失败')
  }
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

.form-card {
  margin-bottom: 20px;
}

.form-actions {
  text-align: center;
  margin-top: 20px;
}

:deep(.el-upload-list) {
  margin-top: 10px;
}
</style> 