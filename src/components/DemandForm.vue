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
        <el-input 
          v-model="formData.marketing_number" 
          :disabled="isEdit"
          placeholder="请输入营销编号"
        />
      </el-form-item>

      <el-form-item label="钉钉号" prop="dingtalk_number">
        <el-input 
          v-model="formData.dingtalk_number"
          :disabled="isEdit"
          placeholder="请输入钉钉号"
        />
      </el-form-item>

      <el-form-item label="ASIN" prop="asin">
        <el-input 
          v-model="formData.asin"
          :disabled="isEdit"
          placeholder="请输入ASIN"
        />
      </el-form-item>

      <el-form-item label="产品型号" prop="model_id">
        <el-select 
          v-model="formData.model_id" 
          placeholder="请选择产品型号"
        >
          <el-option
            v-for="item in modelOptions"
            :key="item.model_id"
            :label="item.model_name"
            :value="item.model_id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="店铺类型" prop="type_id">
        <el-select 
          v-model="formData.type_id" 
          placeholder="请选择店铺类型"
          :disabled="isEdit"
        >
          <el-option
            v-for="item in typeOptions"
            :key="item.type_id"
            :label="item.type_name"
            :value="item.type_id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="平台" prop="platform_id">
        <el-select 
          v-model="formData.platform_id"
          :disabled="isEdit"
        >
          <el-option
            v-for="item in platformOptions"
            :key="item.platform_id"
            :label="item.platform_name"
            :value="item.platform_id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="国家" prop="country_id">
        <el-select 
          v-model="formData.country_id"
          :disabled="isEdit"
        >
          <el-option
            v-for="item in countryOptions"
            :key="item.country_id"
            :label="item.country_name"
            :value="item.country_id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="品牌" prop="brand_id">
        <el-select 
          v-model="formData.brand_id"
          :disabled="isEdit"
        >
          <el-option
            v-for="item in brandOptions"
            :key="item.brand_id"
            :label="item.brand_name"
            :value="item.brand_id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="店铺" prop="store_id">
        <el-select v-model="formData.store_id" placeholder="请选择店铺">
          <el-option
            v-for="item in storeOptions"
            :key="item.store_id"
            :label="item.store_name"
            :value="item.store_id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="账号" prop="account_id">
        <el-select v-model="formData.account_id" placeholder="请选择账号">
          <el-option
            v-for="item in accountOptions"
            :key="item.account_id"
            :label="item.account_name"
            :value="item.account_id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="搜索方式" prop="method_id">
        <el-select v-model="formData.method_id" placeholder="请选择搜索方式">
          <el-option
            v-for="item in methodOptions"
            :key="item.method_id"
            :label="item.method_name"
            :value="item.method_id"
          />
        </el-select>
      </el-form-item>
    </el-card>

    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <span>评估信息</span>
        </div>
      </template>

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
        <el-input v-model="formData.search_keyword" />
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

      <el-form-item label="广告入口" prop="ad_entry_option_id">
        <el-select v-model="formData.ad_entry_option_id" placeholder="请选择广告入口">
          <el-option
            v-for="item in adEntryOptions"
            :key="item.option_id"
            :label="item.option_name"
            :value="item.option_id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="变体选项" prop="variant_option_id">
        <el-select v-model="formData.variant_option_id" placeholder="请选择变体选项">
          <el-option
            v-for="item in variantOptions"
            :key="item.option_id"
            :label="item.option_name"
            :value="item.option_id"
          />
        </el-select>
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
  </el-form>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { getAllOptions } from '@/api/demand'
import { DemandStatus } from '@/types/demand'
import type { 
  ModelOption, TypeOption, PlatformOption, CountryOption,
  BrandOption, StoreOption, AccountOption, MethodOption
} from '@/types/demand'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const formRef = ref<FormInstance>()

// 选项数据
const modelOptions = ref<ModelOption[]>([])
const typeOptions = ref<TypeOption[]>([])
const platformOptions = ref<PlatformOption[]>([])
const countryOptions = ref<CountryOption[]>([])
const brandOptions = ref<BrandOption[]>([])
const storeOptions = ref<StoreOption[]>([])
const accountOptions = ref<AccountOption[]>([])
const methodOptions = ref<MethodOption[]>([])
const adEntryOptions = ref<Array<{ option_id: number; option_name: string }>>([])
const variantOptions = ref<Array<{ option_id: number; option_name: string }>>([])

// 表单数据
const formData = ref({
  marketing_number: '',
  dingtalk_number: '',
  asin: '',
  model_id: undefined as number | undefined,
  type_id: undefined as number | undefined,
  platform_id: undefined as number | undefined,
  country_id: undefined as number | undefined,
  brand_id: undefined as number | undefined,
  store_id: undefined as number | undefined,
  account_id: undefined as number | undefined,
  method_id: undefined as number | undefined,
  assessment_quantity: 0,
  text_review_quantity: 0,
  image_review_quantity: 0,
  video_review_quantity: 0,
  product_price: null as number | null,
  search_keyword: '',
  hyperlink: '',
  other_notes: '',
  status_id: DemandStatus.PENDING,
  ordered_quantity: 0,
  unordered_quantity: 0,
  reviewed_quantity: 0,
  unreviewed_quantity: 0,
  registration_date: null,
  first_order_date: null,
  ad_entry_option_id: undefined as number | undefined,
  variant_option_id: undefined as number | undefined,
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
  model_id: [
    { required: true, message: '请选择评估模式', trigger: 'change' }
  ],
  type_id: [
    { required: true, message: '请选择评估类型', trigger: 'change' }
  ],
  platform_id: [
    { required: true, message: '请选择平台', trigger: 'change' }
  ],
  country_id: [
    { required: true, message: '请选择国家', trigger: 'change' }
  ],
  brand_id: [
    { required: true, message: '请选择品牌', trigger: 'change' }
  ],
  store_id: [
    { required: true, message: '请选择店铺', trigger: 'change' }
  ],
  account_id: [
    { required: true, message: '请选择账号', trigger: 'change' }
  ],
  method_id: [
    { required: true, message: '请选择搜索方式', trigger: 'change' }
  ],
  ad_entry_option_id: [
    { required: true, message: '请选择广告入口', trigger: 'change' }
  ],
  variant_option_id: [
    { required: true, message: '请选择变体选项', trigger: 'change' }
  ]
}

// 加载选项数据
const loadOptions = async () => {
  try {
    const response = await getAllOptions()
    console.log('Options loaded:', response)
    
    if (response) {
      modelOptions.value = response.models || []
      typeOptions.value = response.types || []
      platformOptions.value = response.platforms || []
      countryOptions.value = response.countries || []
      brandOptions.value = response.brands || []
      storeOptions.value = response.stores || []
      accountOptions.value = response.accounts || []
      methodOptions.value = response.methods || []
      adEntryOptions.value = response.adEntryOptions || []
      variantOptions.value = response.variantOptions || []
    }
  } catch (error) {
    console.error('Failed to load options:', error)
    ElMessage.error('加载选项数据失败')
  }
}

// 监听外部数据变化
watch(
  () => props.modelValue,
  (val) => {
    if (val && Object.keys(val).length > 0) {
      console.log('Form received data:', val)
      formData.value = {
        ...formData.value,
        ...val
      }
    }
  },
  { immediate: true, deep: true }
)

// 监听表单数据变化
watch(
  () => formData.value,
  (val) => {
    console.log('Form data changed:', val)
    emit('update:modelValue', val)
  },
  { deep: true }
)

// 确保组件挂载时加载选项
onMounted(async () => {
  await loadOptions()
})

defineExpose({
  validate: () => formRef.value?.validate()
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