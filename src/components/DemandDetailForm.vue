<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="120px"
    class="demand-form"
    v-loading="loading"
  >
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="营销编号" prop="marketing_number">
          <el-input v-model="form.marketing_number" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="钉钉号" prop="dingtalk_number">
          <el-input v-model="form.dingtalk_number" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="ASIN" prop="asin">
          <el-input v-model="form.asin" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="评估数量" prop="assessment_quantity">
          <el-input-number v-model="form.assessment_quantity" :min="1" style="width: 100%" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="文字评论数" prop="text_review_quantity">
          <el-input-number v-model="form.text_review_quantity" :min="0" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="图片评论数" prop="image_review_quantity">
          <el-input-number v-model="form.image_review_quantity" :min="0" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="视频评论数" prop="video_review_quantity">
          <el-input-number v-model="form.video_review_quantity" :min="0" style="width: 100%" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="状态" prop="status_id">
          <el-select v-model="form.status_id" style="width: 100%">
            <el-option
              v-for="item in statusOptions"
              :key="item.status_id"
              :label="item.status_name"
              :value="item.status_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="产品型号" prop="model_id">
          <el-select v-model="form.model_id" style="width: 100%">
            <el-option
              v-for="item in modelOptions"
              :key="item.model_id"
              :label="item.model_name"
              :value="item.model_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="业务类型" prop="type_id">
          <el-select v-model="form.type_id" style="width: 100%">
            <el-option
              v-for="item in typeOptions"
              :key="item.type_id"
              :label="item.type_name"
              :value="item.type_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="平台" prop="platform_id">
          <el-select v-model="form.platform_id" style="width: 100%">
            <el-option
              v-for="item in platformOptions"
              :key="item.platform_id"
              :label="item.platform_name"
              :value="item.platform_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="国家" prop="country_id">
          <el-select v-model="form.country_id" style="width: 100%">
            <el-option
              v-for="item in countryOptions"
              :key="item.country_id"
              :label="item.country_name"
              :value="item.country_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="品牌" prop="brand_id">
          <el-select v-model="form.brand_id" style="width: 100%">
            <el-option
              v-for="item in brandOptions"
              :key="item.brand_id"
              :label="item.brand_name"
              :value="item.brand_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="产品价格" prop="product_price">
          <el-input-number v-model="form.product_price" :precision="2" :step="0.1" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="搜索关键词" prop="search_keyword">
          <el-input v-model="form.search_keyword" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="链接" prop="hyperlink">
      <el-input v-model="form.hyperlink" />
    </el-form-item>

    <el-form-item label="备注" prop="other_notes">
      <el-input
        v-model="form.other_notes"
        type="textarea"
        :rows="3"
      />
    </el-form-item>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="免费评论数" prop="free_review_quantity">
          <el-input-number v-model="form.free_review_quantity" :min="0" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="点赞数量" prop="like_only_quantity">
          <el-input-number v-model="form.like_only_quantity" :min="0" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="FB订单数量" prop="fb_order_quantity">
          <el-input-number v-model="form.fb_order_quantity" :min="0" style="width: 100%" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="6">
        <el-form-item label="已下单数量" prop="ordered_quantity">
          <el-input-number v-model="form.ordered_quantity" :min="0" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="6">
        <el-form-item label="未下单数量" prop="unordered_quantity">
          <el-input-number v-model="form.unordered_quantity" :min="0" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="6">
        <el-form-item label="已评论数量" prop="reviewed_quantity">
          <el-input-number v-model="form.reviewed_quantity" :min="0" style="width: 100%" />
        </el-form-item>
      </el-col>
      <el-col :span="6">
        <el-form-item label="未评论数量" prop="unreviewed_quantity">
          <el-input-number v-model="form.unreviewed_quantity" :min="0" style="width: 100%" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="注册日期" prop="registration_date">
          <el-date-picker
            v-model="form.registration_date"
            type="date"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="首单日期" prop="first_order_date">
          <el-date-picker
            v-model="form.first_order_date"
            type="date"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="店铺" prop="store_id">
          <el-select v-model="form.store_id" style="width: 100%">
            <el-option
              v-for="item in storeOptions"
              :key="item.store_id"
              :label="item.store_name"
              :value="item.store_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="账号" prop="account_id">
          <el-select v-model="form.account_id" style="width: 100%">
            <el-option
              v-for="item in accountOptions"
              :key="item.account_id"
              :label="item.account_name"
              :value="item.account_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="搜索方式" prop="method_id">
          <el-select v-model="form.method_id" style="width: 100%">
            <el-option
              v-for="item in methodOptions"
              :key="item.method_id"
              :label="item.method_name"
              :value="item.method_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="广告入口" prop="ad_entry_option_id">
          <el-select v-model="form.ad_entry_option_id" style="width: 100%">
            <el-option
              v-for="item in adEntryOptions"
              :key="item.option_id"
              :label="item.option_name"
              :value="item.option_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="变体选项" prop="variant_option_id">
          <el-select v-model="form.variant_option_id" style="width: 100%">
            <el-option
              v-for="item in variantOptions"
              :key="item.option_id"
              :label="item.option_name"
              :value="item.option_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="产品图片" prop="product_image_url">
          <el-input v-model="form.product_image_url" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="收到产品图片" prop="received_product_image_url">
          <el-input v-model="form.received_product_image_url" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="订单样式" prop="order_style">
          <el-input v-model="form.order_style" />
        </el-form-item>
      </el-col>
      <el-col :span="6">
        <el-form-item label="属性值1" prop="attribute_value_1">
          <el-input v-model="form.attribute_value_1" />
        </el-form-item>
      </el-col>
      <el-col :span="6">
        <el-form-item label="属性值2" prop="attribute_value_2">
          <el-input v-model="form.attribute_value_2" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">中介信息</el-divider>
    
    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="分配中介" prop="intermediary_id">
          <el-select 
            v-model="form.intermediary_id" 
            style="width: 100%"
            clearable
            placeholder="请选择中介"
          >
            <el-option
              v-for="item in intermediaryOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="中介状态" prop="intermediary_status">
          <el-select 
            v-model="form.intermediary_status" 
            style="width: 100%"
            :disabled="!form.intermediary_id"
          >
            <el-option
              v-for="item in intermediaryStatusOptions"
              :key="item.status_id"
              :label="item.status_name"
              :value="item.status_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="支付状态" prop="payment_status">
          <el-select 
            v-model="form.payment_status" 
            style="width: 100%"
            :disabled="!form.intermediary_id"
          >
            <el-option
              v-for="item in paymentStatusOptions"
              :key="item.status_id"
              :label="item.status_name"
              :value="item.status_id"
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="分配时间" prop="assignment_time">
          <el-date-picker
            v-model="form.assignment_time"
            type="datetime"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled="!form.intermediary_id"
          />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="完成时间" prop="completion_time">
          <el-date-picker
            v-model="form.completion_time"
            type="datetime"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled="!form.intermediary_id"
          />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="支付时间" prop="payment_time">
          <el-date-picker
            v-model="form.payment_time"
            type="datetime"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled="!form.intermediary_id"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="支付金额" prop="payment_amount">
          <el-input-number
            v-model="form.payment_amount"
            :precision="2"
            :step="0.1"
            style="width: 100%"
            :disabled="!form.intermediary_id"
          />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="中介备注" prop="intermediary_remark">
          <el-input
            v-model="form.intermediary_remark"
            type="textarea"
            :rows="2"
            :disabled="!form.intermediary_id"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item>
      <el-button 
        type="primary" 
        @click="submitForm"
        :loading="submitting"
      >
        {{ submitting ? '提交中...' : '提交' }}
      </el-button>
      <el-button @click="resetForm" :disabled="submitting">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import axios from 'axios'
import type { 
  DemandForm as DemandFormType,
  StatusOption,
  ModelOption,
  TypeOption,
  PlatformOption,
  CountryOption,
  BrandOption,
  StoreOption,
  AccountOption,
  MethodOption,
  AdEntryOption,
  VariantOption,
  Intermediary,
  IntermediaryStatusOption,
  PaymentStatusOption
} from '../types/demand'
import { isValidUrl, isPositiveNumber, isNonNegativeNumber } from '../utils/validators'

const props = defineProps<{
  initialData?: Partial<DemandFormType>
}>()

const emit = defineEmits(['submit'])

const formRef = ref<FormInstance>()
const form = ref<DemandFormType>({
  marketing_number: '',
  dingtalk_number: '',
  asin: '',
  assessment_quantity: 1,
  text_review_quantity: 0,
  image_review_quantity: 0,
  video_review_quantity: 0,
  product_price: null,
  search_keyword: '',
  hyperlink: '',
  other_notes: '',
  status_id: 1,
  model_id: 1,
  type_id: 1,
  platform_id: 1,
  country_id: 1,
  brand_id: 1,
  store_id: 1,
  account_id: 1,
  method_id: 1,
  ad_entry_option_id: 1,
  variant_option_id: 1,
  free_review_quantity: 0,
  like_only_quantity: 0,
  fb_order_quantity: 0,
  ordered_quantity: 0,
  unordered_quantity: 0,
  reviewed_quantity: 0,
  unreviewed_quantity: 0,
  registration_date: null,
  first_order_date: null,
  product_image_url: '',
  received_product_image_url: '',
  order_style: '',
  attribute_value_1: '',
  attribute_value_2: '',
  intermediary_id: null,
  intermediary_status: 1,
  intermediary_remark: '',
  assignment_time: null,
  completion_time: null,
  payment_amount: null,
  payment_time: null,
  payment_status: 1
})

const statusOptions = ref<StatusOption[]>([])
const modelOptions = ref<ModelOption[]>([])
const typeOptions = ref<TypeOption[]>([])
const platformOptions = ref<PlatformOption[]>([])
const countryOptions = ref<CountryOption[]>([])
const brandOptions = ref<BrandOption[]>([])
const storeOptions = ref<StoreOption[]>([])
const accountOptions = ref<AccountOption[]>([])
const methodOptions = ref<MethodOption[]>([])
const adEntryOptions = ref<AdEntryOption[]>([])
const variantOptions = ref<VariantOption[]>([])
const intermediaryOptions = ref<Intermediary[]>([])
const intermediaryStatusOptions = ref<IntermediaryStatusOption[]>([])
const paymentStatusOptions = ref<PaymentStatusOption[]>([])

const loading = ref(false)
const submitting = ref(false)

const rules = {
  marketing_number: [
    { required: true, message: '请输入营销编号', trigger: 'blur' },
    { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  dingtalk_number: [
    { required: true, message: '请输入钉钉号', trigger: 'blur' },
    { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  asin: [
    { required: true, message: '请输入ASIN', trigger: 'blur' },
    { min: 1, max: 20, message: 'ASIN长度在 1 到 20 个字符', trigger: 'blur' }
  ],
  assessment_quantity: [
    { required: true, message: '请输入评估数量', trigger: 'blur' },
    { validator: (_, value) => isPositiveNumber(value) ? Promise.resolve() : Promise.reject('评估数量必须大于0'), trigger: 'blur' }
  ],
  text_review_quantity: [
    { validator: (_, value) => isNonNegativeNumber(value) ? Promise.resolve() : Promise.reject('评论数量不能为负数'), trigger: 'blur' }
  ],
  image_review_quantity: [
    { validator: (_, value) => isNonNegativeNumber(value) ? Promise.resolve() : Promise.reject('评论数量不能为负数'), trigger: 'blur' }
  ],
  video_review_quantity: [
    { validator: (_, value) => isNonNegativeNumber(value) ? Promise.resolve() : Promise.reject('评论数量不能为负数'), trigger: 'blur' }
  ],
  product_price: [
    { validator: (_, value) => !value || value > 0 ? Promise.resolve() : Promise.reject('价格必须大于0'), trigger: 'blur' }
  ],
  hyperlink: [
    { validator: (_, value) => !value || isValidUrl(value) ? Promise.resolve() : Promise.reject('请输入有效的URL'), trigger: 'blur' }
  ],
  status_id: [{ required: true, message: '请选择状态', trigger: 'change' }],
  model_id: [{ required: true, message: '请选择产品型号', trigger: 'change' }],
  type_id: [{ required: true, message: '请选择业务类型', trigger: 'change' }],
  platform_id: [{ required: true, message: '请选择平台', trigger: 'change' }],
  country_id: [{ required: true, message: '请选择国家', trigger: 'change' }],
  brand_id: [{ required: true, message: '请选择品牌', trigger: 'change' }],
  store_id: [{ required: true, message: '请选择店铺', trigger: 'change' }],
  account_id: [{ required: true, message: '请选择账号', trigger: 'change' }],
  method_id: [{ required: true, message: '请选择搜索方式', trigger: 'change' }],
  ad_entry_option_id: [{ required: true, message: '请选择广告入口', trigger: 'change' }],
  variant_option_id: [{ required: true, message: '请选择变体选项', trigger: 'change' }]
}

const loadOptions = async () => {
  loading.value = true
  try {
    const { data } = await axios.get('/api/options')
    
    // 更新选项数据
    statusOptions.value = data.status || []
    modelOptions.value = data.models || []
    typeOptions.value = data.types || []
    platformOptions.value = data.platforms || []
    countryOptions.value = data.countries || []
    brandOptions.value = data.brands || []
    storeOptions.value = data.stores || []
    accountOptions.value = data.accounts || []
    methodOptions.value = data.methods || []
    adEntryOptions.value = data.adEntryOptions || []
    variantOptions.value = data.variantOptions || []
    
  } catch (error) {
    console.error('Error loading options:', error)
    ElMessage.error('加载选项数据失败，请刷新页面重试')
  } finally {
    loading.value = false
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    submitting.value = true
    await formRef.value.validate((valid) => {
      if (valid) {
        emit('submit', form.value)
      }
    })
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  if (!formRef.value) return
  formRef.value.resetFields()
}

const handleIntermediaryChange = () => {
  if (!form.value.intermediary_id) {
    form.value.intermediary_status = 1
    form.value.payment_status = 1
    form.value.assignment_time = null
    form.value.completion_time = null
    form.value.payment_amount = null
    form.value.payment_time = null
    form.value.intermediary_remark = ''
  }
}

onMounted(() => {
  loadOptions()
  if (props.initialData) {
    form.value = { ...form.value, ...props.initialData }
  }
})
</script>

<style scoped>
.demand-form {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style> 