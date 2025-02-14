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

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="营销编号" prop="marketing_number">
            <el-input v-model="formData.marketing_number" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="钉钉号" prop="dingtalk_number">
            <el-input v-model="formData.dingtalk_number" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="ASIN" prop="asin">
            <el-input v-model="formData.asin" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="产品型号" prop="model_id">
            <el-select 
              v-model="formData.model_id"
              placeholder="请选择产品型号"
              style="width: 100%"
            >
              <el-option
                v-for="item in options.models"
                :key="item.model_id"
                :label="item.model_name"
                :value="item.model_id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="店铺类型" prop="type_id">
            <el-select v-model="formData.type_id" placeholder="请选择店铺类型" style="width: 100%">
              <el-option
                v-for="item in options.types"
                :key="item.type_id"
                :label="item.type_name"
                :value="item.type_id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="平台" prop="platform_id">
            <el-select v-model="formData.platform_id" placeholder="请选择平台" style="width: 100%">
              <el-option
                v-for="item in options.platforms"
                :key="item.platform_id"
                :label="item.platform_name"
                :value="item.platform_id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="国家" prop="country_id">
            <el-select v-model="formData.country_id" placeholder="请选择国家" style="width: 100%">
              <el-option
                v-for="item in options.countries"
                :key="item.country_id"
                :label="item.country_name"
                :value="item.country_id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="品牌" prop="brand_id">
            <el-select v-model="formData.brand_id" placeholder="请选择品牌" style="width: 100%">
              <el-option
                v-for="item in options.brands"
                :key="item.brand_id"
                :label="item.brand_name"
                :value="item.brand_id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="店铺" prop="store_id">
            <el-select v-model="formData.store_id" placeholder="请选择店铺" style="width: 100%">
              <el-option
                v-for="item in options.stores"
                :key="item.store_id"
                :label="item.store_name"
                :value="item.store_id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="搜索方式" prop="method_id">
            <el-select v-model="formData.method_id" placeholder="请选择搜索方式" style="width: 100%">
              <el-option
                v-for="item in options.methods"
                :key="item.method_id"
                :label="item.method_name"
                :value="item.method_id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <span>评估信息</span>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <el-form-item label="评估数量" prop="assessment_quantity">
            <el-input-number v-model="formData.assessment_quantity" :min="0" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="文字评论" prop="text_review_quantity">
            <el-input-number v-model="formData.text_review_quantity" :min="0" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="图片评论" prop="image_review_quantity">
            <el-input-number v-model="formData.image_review_quantity" :min="0" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="视频评论" prop="video_review_quantity">
            <el-input-number v-model="formData.video_review_quantity" :min="0" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
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
const options = ref({
  models: [],
  types: [],
  platforms: [],
  countries: [],
  brands: [],
  stores: [],
  accounts: [],
  methods: []
})

// 创建本地表单数据的副本
const formData = ref({ ...props.modelValue })

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
      options.value = {
        models: response.models || [],
        types: response.types || [],
        platforms: response.platforms || [],
        countries: response.countries || [],
        brands: response.brands || [],
        stores: response.stores || [],
        accounts: response.accounts || [],
        methods: response.methods || []
      }
    }
  } catch (error) {
    console.error('Failed to load options:', error)
    ElMessage.error('加载选项数据失败')
  }
}

// 监听表单数据变化并同步到父组件
watch(
  formData,
  (newVal) => {
    console.log('Form data changed:', newVal)
    emit('update:modelValue', { ...newVal })
  },
  { deep: true }
)

// 监听外部数据变化并更新本地表单
watch(
  () => props.modelValue,
  (newVal) => {
    console.log('Props changed:', newVal)
    formData.value = { ...newVal }
  },
  { deep: true }
)

onMounted(() => {
  loadOptions()
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

.card-header {
  font-weight: bold;
}
</style> 