<template>
  <div class="create-payment">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <h2>录入返款明细</h2>
        </div>
      </template>

      <el-form 
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="payment-form"
      >
        <!-- 订单信息 -->
        <el-form-item label="订单号" prop="order_number">
          <el-input v-model="form.order_number" placeholder="请输入测评明细中的订单号" />
        </el-form-item>

        <!-- 返款信息 -->
        <el-form-item label="客户邮箱" prop="customer_email">
          <el-input v-model="form.customer_email" placeholder="请输入客户邮箱" />
        </el-form-item>

        <el-form-item label="订单金额" prop="order_amount">
          <el-input-number 
            v-model="form.order_amount"
            :precision="2"
            :step="0.1"
            :min="0"
            style="width: 180px"
          />
          <el-select v-model="form.currency" style="margin-left: 10px; width: 100px">
            <el-option label="USD" value="USD" />
            <el-option label="CNY" value="CNY" />
          </el-select>
        </el-form-item>

        <el-form-item label="实际转账金额" prop="transfer_amount">
          <el-input-number 
            v-model="form.transfer_amount"
            :precision="2"
            :step="0.1"
            :min="0"
          />
        </el-form-item>

        <el-form-item label="中介佣金" prop="intermediary_commission">
          <el-input-number 
            v-model="form.intermediary_commission"
            :precision="2"
            :step="0.1"
            :min="0"
          />
        </el-form-item>

        <el-form-item label="RMB佣金" prop="rmb_commission">
          <el-input-number 
            v-model="form.rmb_commission"
            :precision="2"
            :step="0.1"
            :min="0"
          />
          <span style="margin-left: 10px">CNY</span>
        </el-form-item>

        <el-form-item label="支付方式" prop="payment_method">
          <el-select v-model="form.payment_method" placeholder="请选择支付方式">
            <el-option label="PayPal" value="PayPal" />
            <el-option label="银行卡" value="银行卡" />
            <el-option label="支付宝" value="支付宝" />
            <el-option label="微信" value="微信" />
          </el-select>
        </el-form-item>

        <el-form-item label="支付账号" prop="payment_account">
          <el-input v-model="form.payment_account" placeholder="请输入支付账号" />
        </el-form-item>

        <el-form-item label="支付时间" prop="payment_time">
          <el-date-picker
            v-model="form.payment_time"
            type="datetime"
            placeholder="请选择支付时间"
          />
        </el-form-item>

        <el-form-item label="支付截图" prop="payment_screenshot">
          <el-upload
            class="upload-demo"
            action="/api/upload/image"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            accept=".jpg,.jpeg,.png,.gif"
          >
            <el-button type="primary">点击上传</el-button>
            <template #tip>
              <div class="el-upload__tip">
                只能上传 jpg/png/gif 文件
              </div>
            </template>
          </el-upload>
          <div v-if="form.payment_screenshot" class="image-preview">
            <el-image 
              :src="form.payment_screenshot"
              :preview-src-list="[form.payment_screenshot]"
              fit="cover"
              class="preview-image"
            />
            <el-button 
              type="danger" 
              size="small"
              class="delete-btn"
              @click="handleRemoveImage"
            >
              删除
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input 
            v-model="form.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit">提交</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import axios from 'axios'
import { refundApi } from '@/api/refund'

const router = useRouter()
const formRef = ref<FormInstance>()

const form = reactive({
  order_number: '',
  customer_email: '',
  order_amount: 0,
  currency: 'USD',
  transfer_amount: 0,
  intermediary_commission: 0,
  rmb_commission: 0,
  payment_method: '',
  payment_account: '',
  payment_time: null,
  payment_screenshot: '',
  remark: ''
})

const rules = reactive<FormRules>({
  order_number: [
    { required: true, message: '请输入订单号', trigger: 'blur' }
  ],
  customer_email: [
    { required: true, message: '请输入客户邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  order_amount: [
    { required: true, message: '请输入订单金额', trigger: 'blur' }
  ],
  transfer_amount: [
    { required: true, message: '请输入实际转账金额', trigger: 'blur' }
  ],
  payment_method: [
    { required: true, message: '请选择支付方式', trigger: 'change' }
  ],
  payment_account: [
    { required: true, message: '请输入支付账号', trigger: 'blur' }
  ],
  payment_time: [
    { required: true, message: '请选择支付时间', trigger: 'change' }
  ],
  payment_screenshot: [
    { required: true, message: '请上传支付截图', trigger: 'change' }
  ]
})

// 上传相关方法
const beforeUpload = (file: File) => {
  const isImage = /\.(jpg|jpeg|png|gif)$/i.test(file.name)
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

const handleUploadSuccess = (response: any) => {
  if (response.code === 0) {
    form.payment_screenshot = response.data.url
    ElMessage.success('上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

const handleUploadError = () => {
  ElMessage.error('上传失败')
}

const handleRemoveImage = () => {
  form.payment_screenshot = ''
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    const { data: response } = await axios.post(refundApi.createPayment, {
      ...form,
      payment_time: form.payment_time ? new Date(form.payment_time).toISOString() : null
    })
    
    if (response.code === 0) {
      ElMessage.success('创建成功')
      router.push('/refunds')
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    console.error('Error submitting form:', error)
    ElMessage.error('提交失败')
  }
}
</script>

<style scoped>
.create-payment {
  padding: 20px;
}

.form-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.payment-form {
  margin-top: 20px;
}

:deep(.el-input-number) {
  width: 100%;
}

.image-preview {
  margin-top: 10px;
  position: relative;
  display: inline-block;
}

.preview-image {
  width: 150px;
  height: 150px;
  border-radius: 4px;
}

.delete-btn {
  position: absolute;
  right: 5px;
  top: 5px;
}
</style> 