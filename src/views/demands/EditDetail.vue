<template>
  <div class="edit-detail">
    <div class="header">
      <h2>编辑测评明细</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>

    <el-form
      v-loading="loading"
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
    >
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
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
          />
        </el-form-item>

        <el-form-item label="下单时间" prop="order_time">
          <el-date-picker
            v-model="formData.order_time"
            type="datetime"
            placeholder="选择下单时间"
          />
        </el-form-item>

        <el-form-item label="评论时间" prop="review_time">
          <el-date-picker
            v-model="formData.review_time"
            type="datetime"
            placeholder="选择评论时间"
          />
        </el-form-item>

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

      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>评论内容</span>
          </div>
        </template>

        <el-form-item label="评论内容" prop="review_content">
          <el-input
            v-model="formData.review_content"
            type="textarea"
            :rows="4"
          />
        </el-form-item>

        <el-form-item label="评论图片">
          <UploadImage
            v-model:value="formData.review_images"
            :limit="5"
            multiple
          />
        </el-form-item>

        <el-form-item label="评论视频">
          <UploadVideo v-model:value="formData.review_video" />
        </el-form-item>
      </el-card>

      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>截图信息</span>
          </div>
        </template>

        <el-form-item label="支付截图">
          <UploadImage v-model:value="formData.payment_screenshot" />
        </el-form-item>

        <el-form-item label="订单截图">
          <UploadImage v-model:value="formData.order_screenshot" />
        </el-form-item>

        <el-form-item label="评论截图">
          <UploadImage v-model:value="formData.review_screenshot" />
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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { demandApi } from '@/api/demand'
import { DetailStatus } from '@/types/detail'
import UploadImage from '@/components/UploadImage.vue'
import UploadVideo from '@/components/UploadVideo.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const formRef = ref<FormInstance>()

const formData = ref({
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
  ]
}

const loadDetail = async () => {
  try {
    loading.value = true
    const data = await demandApi.getDetailById(Number(route.params.detailId))
    formData.value = {
      ...formData.value,
      ...data
    }
  } catch (error) {
    console.error('Failed to load detail:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    await demandApi.updateDetail(Number(route.params.detailId), formData.value)
    ElMessage.success('保存成功')
    router.back()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to update detail:', error)
      ElMessage.error('保存失败')
    }
  } finally {
    loading.value = false
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

.form-card {
  margin-bottom: 20px;
}

.form-actions {
  margin-top: 20px;
  text-align: center;
}
</style> 