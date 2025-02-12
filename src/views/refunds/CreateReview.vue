<template>
  <div class="create-review">
    <div class="header">
      <h2>录入评价明细</h2>
      <el-button @click="router.back()">返回</el-button>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      class="review-form"
    >
      <!-- 选择关联订单 -->
      <el-form-item label="选择订单" prop="order_id">
        <el-select
          v-model="form.order_id"
          filterable
          remote
          :remote-method="searchOrders"
          :loading="loading"
          placeholder="请输入营销编号/订单号搜索"
          @change="handleOrderChange"
        >
          <el-option
            v-for="item in orders"
            :key="item.id"
            :label="`${item.marketing_number} - ${item.order_number}`"
            :value="item.id"
          />
        </el-select>
      </el-form-item>

      <!-- 评价信息 -->
      <el-divider content-position="left">评价信息</el-divider>

      <el-form-item label="评价性质" prop="review_type">
        <el-select v-model="form.review_type" placeholder="请选择评价性质">
          <el-option label="文字评价" value="text" />
          <el-option label="图片评价" value="image" />
          <el-option label="视频评价" value="video" />
        </el-select>
      </el-form-item>

      <el-form-item label="评价链接" prop="review_link">
        <el-input
          v-model="form.review_link"
          placeholder="请输入评价链接"
          type="url"
        />
      </el-form-item>

      <!-- 评价截图 -->
      <el-form-item label="评价截图一" prop="screenshot1">
        <upload-image
          v-model="form.screenshot1"
          :auto-upload="true"
          :show-file-list="false"
          accept="image/*"
          :limit="1"
          :on-success="(url) => handleUploadSuccess(url, 'screenshot1')"
        />
        <div class="upload-tip">自动匹配评价命名格式-1</div>
      </el-form-item>

      <el-form-item label="评价截图二" prop="screenshot2">
        <upload-image
          v-model="form.screenshot2"
          :auto-upload="true"
          :show-file-list="false"
          accept="image/*"
          :limit="1"
          :on-success="(url) => handleUploadSuccess(url, 'screenshot2')"
        />
        <div class="upload-tip">自动匹配评价命名格式-2</div>
      </el-form-item>

      <el-form-item label="备注" prop="remark">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="3"
          placeholder="请输入备注信息"
        />
      </el-form-item>

      <!-- 按钮组 -->
      <el-form-item>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button @click="router.back()">返回</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import type { RefundReview, RefundOrder } from '@/types/refund'
import UploadImage from '@/components/UploadImage.vue'
import axios from 'axios'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)
const orders = ref<RefundOrder[]>([])

// 表单数据
const form = ref<Partial<RefundReview>>({
  review_type: 'text'
})

// 表单验证规则
const rules: FormRules = {
  order_id: [
    { required: true, message: '请选择关联订单', trigger: 'change' }
  ],
  review_type: [
    { required: true, message: '请选择评价性质', trigger: 'change' }
  ],
  review_link: [
    { required: true, message: '请输入评价链接', trigger: 'blur' },
    { type: 'url', message: '请输入正确的URL格式', trigger: 'blur' }
  ]
}

// 搜索订单
const searchOrders = async (query: string) => {
  if (!query) return
  
  try {
    loading.value = true
    const { data: response } = await axios.get('/api/refunds/orders/search', {
      params: { keyword: query }
    })
    
    if (response.code === 0) {
      orders.value = response.data
    }
  } catch (error) {
    console.error('Failed to search orders:', error)
  } finally {
    loading.value = false
  }
}

// 订单变更处理
const handleOrderChange = async (orderId: number) => {
  if (!orderId) return
  
  const order = orders.value.find(o => o.id === orderId)
  if (order) {
    form.value = {
      ...form.value,
      order_id: order.id,
      detail_id: order.detail_id
    }
  }
}

// 上传成功处理
const handleUploadSuccess = (url: string, field: 'screenshot1' | 'screenshot2') => {
  form.value[field] = url
}

// 提交处理
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const { data: response } = await axios.post('/api/refunds/reviews', form.value)
    
    if (response.code === 0) {
      ElMessage.success('创建成功')
      router.back()
    } else {
      ElMessage.error(response.message || '创建失败')
    }
  } catch (error) {
    console.error('Failed to create review:', error)
    ElMessage.error('创建失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const handleReset = () => {
  formRef.value?.resetFields()
  form.value = {
    review_type: 'text'
  }
}
</script>

<style scoped>
.create-review {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.review-form {
  max-width: 800px;
}

.upload-tip {
  margin-top: 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

:deep(.el-divider__text) {
  font-size: 16px;
  font-weight: bold;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-textarea__inner) {
  min-height: 80px;
}
</style> 