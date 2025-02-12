<template>
  <div class="create-order">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <h2>录入返款订单</h2>
        </div>
      </template>

      <el-form 
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="order-form"
      >
        <!-- 订单基本信息 -->
        <el-form-item label="订单号" prop="order_number">
          <el-input v-model="form.order_number" placeholder="请输入测评明细中的订单号" />
        </el-form-item>

        <el-form-item label="营销编号" prop="marketing_number">
          <el-input v-model="form.marketing_number" placeholder="请输入营销编号" />
        </el-form-item>

        <el-form-item label="钉钉号" prop="dingtalk_number">
          <el-input v-model="form.dingtalk_number" placeholder="请输入钉钉号" />
        </el-form-item>

        <el-form-item label="商品ASIN" prop="asin">
          <el-input v-model="form.asin" placeholder="请输入商品ASIN" />
        </el-form-item>

        <el-form-item label="中介名称" prop="intermediary">
          <el-input v-model="form.intermediary" placeholder="请输入中介名称" />
        </el-form-item>

        <el-form-item label="下单日期" prop="order_date">
          <el-date-picker
            v-model="form.order_date"
            type="datetime"
            placeholder="请选择下单日期"
          />
        </el-form-item>

        <el-form-item label="订单金额" prop="order_amount">
          <el-input-number 
            v-model="form.order_amount"
            :precision="2"
            :step="0.1"
            :min="0"
          />
        </el-form-item>

        <el-form-item label="币种" prop="currency">
          <el-select v-model="form.currency" placeholder="请选择币种">
            <el-option label="USD" value="USD" />
            <el-option label="CNY" value="CNY" />
          </el-select>
        </el-form-item>

        <el-form-item label="评价类型" prop="review_type">
          <el-select v-model="form.review_type" placeholder="请选择评价类型">
            <el-option label="文字" value="text" />
            <el-option label="图片" value="image" />
            <el-option label="视频" value="video" />
          </el-select>
        </el-form-item>

        <el-form-item label="业务类型" prop="business_type">
          <el-select v-model="form.business_type" placeholder="请选择业务类型">
            <el-option label="联营" value="joint" />
            <el-option label="自营" value="self" />
          </el-select>
        </el-form-item>

        <el-form-item label="品牌" prop="brand">
          <el-input v-model="form.brand" placeholder="请输入品牌" />
        </el-form-item>

        <!-- 支付信息 -->
        <el-form-item label="支付方式" prop="payment_method">
          <el-select v-model="form.payment_method" placeholder="请选择支付方式">
            <el-option label="PayPal" value="PayPal" />
            <el-option label="银行卡" value="银行卡" />
          </el-select>
        </el-form-item>

        <el-form-item label="PayPal本金" prop="paypal_principal">
          <el-input-number 
            v-model="form.paypal_principal"
            :precision="2"
            :step="0.1"
            :min="0"
          />
        </el-form-item>

        <el-form-item label="人民币佣金" prop="rmb_commission">
          <el-input-number 
            v-model="form.rmb_commission"
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

        <el-form-item label="佣金币种" prop="commission_currency">
          <el-select v-model="form.commission_currency" placeholder="请选择佣金币种">
            <el-option label="USD" value="USD" />
            <el-option label="CNY" value="CNY" />
          </el-select>
        </el-form-item>

        <el-form-item label="汇率" prop="exchange_rate">
          <el-input-number 
            v-model="form.exchange_rate"
            :precision="4"
            :step="0.0001"
            :min="0"
          />
        </el-form-item>

        <el-form-item label="实际支付金额" prop="actual_payment">
          <el-input-number 
            v-model="form.actual_payment"
            :precision="2"
            :step="0.1"
            :min="0"
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

const router = useRouter()
const formRef = ref<FormInstance>()

const form = reactive({
  order_number: '',
  marketing_number: '',
  dingtalk_number: '',
  asin: '',
  intermediary: '',
  order_date: null,
  order_amount: 0,
  currency: 'USD',
  review_type: '',
  business_type: '',
  brand: '',
  payment_method: '',
  paypal_principal: 0,
  rmb_commission: 0,
  intermediary_commission: 0,
  commission_currency: '',
  exchange_rate: 0,
  actual_payment: 0
})

const rules = reactive<FormRules>({
  order_number: [
    { required: true, message: '请输入订单号', trigger: 'blur' }
  ],
  marketing_number: [
    { required: true, message: '请输入营销编号', trigger: 'blur' }
  ],
  dingtalk_number: [
    { required: true, message: '请输入钉钉号', trigger: 'blur' }
  ],
  asin: [
    { required: true, message: '请输入商品ASIN', trigger: 'blur' }
  ],
  order_date: [
    { required: true, message: '请选择下单日期', trigger: 'change' }
  ],
  order_amount: [
    { required: true, message: '请输入订单金额', trigger: 'blur' }
  ],
  currency: [
    { required: true, message: '请选择币种', trigger: 'change' }
  ],
  review_type: [
    { required: true, message: '请选择评价类型', trigger: 'change' }
  ],
  business_type: [
    { required: true, message: '请选择业务类型', trigger: 'change' }
  ],
  brand: [
    { required: true, message: '请输入品牌', trigger: 'blur' }
  ],
  payment_method: [
    { required: true, message: '请选择支付方式', trigger: 'change' }
  ]
})

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    const { data: response } = await axios.post('/api/refund/orders', form)
    
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
.create-order {
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

.order-form {
  margin-top: 20px;
}

:deep(.el-input-number) {
  width: 100%;
}
</style> 