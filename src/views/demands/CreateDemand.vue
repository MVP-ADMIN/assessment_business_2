<template>
  <div class="create-demand">
    <div class="header">
      <h2>创建需求</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>
    
    <el-card v-loading="loading">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
      >
        <!-- 基本信息 -->
        <div class="form-section">
          <h3>基本信息</h3>
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
                <el-select v-model="formData.model_id" style="width: 100%">
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
                <el-select v-model="formData.type_id" style="width: 100%">
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
                <el-select v-model="formData.platform_id" style="width: 100%">
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
                <el-select v-model="formData.country_id" style="width: 100%">
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
              <el-form-item label="账号" prop="account_id">
                <el-select v-model="formData.account_id" style="width: 100%">
                  <el-option
                    v-for="item in options.accounts"
                    :key="item.account_id"
                    :label="item.account_name"
                    :value="item.account_id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="品牌" prop="brand_id">
                <el-select v-model="formData.brand_id" style="width: 100%">
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
                <el-select v-model="formData.store_id" style="width: 100%">
                  <el-option
                    v-for="item in options.stores"
                    :key="item.store_id"
                    :label="item.store_name"
                    :value="item.store_id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="搜索方式" prop="method_id">
                <el-select v-model="formData.method_id" style="width: 100%">
                  <el-option
                    v-for="item in options.methods"
                    :key="item.method_id"
                    :label="item.method_name"
                    :value="item.method_id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="广告入口" prop="ad_entry_option_id">
                <el-select v-model="formData.ad_entry_option_id" style="width: 100%">
                  <el-option
                    v-for="item in options.adEntryOptions"
                    :key="item.option_id"
                    :label="item.option_name"
                    :value="item.option_id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="变体选项" prop="variant_option_id">
                <el-select v-model="formData.variant_option_id" style="width: 100%">
                  <el-option
                    v-for="item in options.variantOptions"
                    :key="item.option_id"
                    :label="item.option_name"
                    :value="item.option_id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 测评信息 -->
        <div class="form-section">
          <h3>测评信息</h3>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="测评数量" prop="assessment_quantity">
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
        </div>

        <!-- 其他信息 -->
        <div class="form-section">
          <h3>其他信息</h3>
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
        </div>
      </el-form>

      <div class="form-actions">
        <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { getAllOptions, createDemand } from '@/api/demand'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)

// 表单数据
const formData = ref({
  marketing_number: '',
  dingtalk_number: '',
  asin: '',
  model_id: null,
  type_id: null,
  platform_id: null,
  country_id: null,
  brand_id: null,
  store_id: null,
  account_id: null,
  method_id: null,
  assessment_quantity: 0,
  text_review_quantity: 0,
  image_review_quantity: 0,
  video_review_quantity: 0,
  product_price: null,
  search_keyword: '',
  hyperlink: '',
  other_notes: '',
  status_id: 1,
  ad_entry_option_id: null,
  variant_option_id: null
})

// 选项数据
const options = ref({
  models: [],
  types: [],
  platforms: [],
  countries: [],
  brands: [],
  stores: [],
  accounts: [],
  methods: [],
  adEntryOptions: [],
  variantOptions: []
})

// 表单验证规则
const rules = {
  marketing_number: [{ required: true, message: '请输入营销编号', trigger: 'blur' }],
  dingtalk_number: [{ required: true, message: '请输入钉钉号', trigger: 'blur' }],
  asin: [{ required: true, message: '请输入ASIN', trigger: 'blur' }],
  model_id: [{ required: true, message: '请选择产品型号', trigger: 'change' }],
  type_id: [{ required: true, message: '请选择店铺类型', trigger: 'change' }],
  platform_id: [{ required: true, message: '请选择平台', trigger: 'change' }],
  country_id: [{ required: true, message: '请选择国家', trigger: 'change' }],
  brand_id: [{ required: true, message: '请选择品牌', trigger: 'change' }],
  store_id: [{ required: true, message: '请选择店铺', trigger: 'change' }],
  account_id: [{ required: true, message: '请选择账号', trigger: 'change' }],
  method_id: [{ required: true, message: '请选择搜索方式', trigger: 'change' }],
  ad_entry_option_id: [{ required: true, message: '请选择广告入口', trigger: 'change' }],
  variant_option_id: [{ required: true, message: '请选择变体选项', trigger: 'change' }]
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
        methods: response.methods || [],
        adEntryOptions: response.adEntryOptions || [],
        variantOptions: response.variantOptions || []
      }
      console.log('Options set:', options.value)
    }
  } catch (error) {
    console.error('Failed to load options:', error)
    ElMessage.error('加载选项数据失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 检查必填字段
    if (!formData.value.account_id) {
      ElMessage.error('请选择账号')
      return
    }
    if (!formData.value.ad_entry_option_id) {
      ElMessage.error('请选择广告入口')
      return
    }
    if (!formData.value.variant_option_id) {
      ElMessage.error('请选择变体选项')
      return
    }
    
    loading.value = true
    console.log('Submitting data:', formData.value)
    
    const response = await createDemand(formData.value)
    if (response.code === 0) {
      ElMessage.success('创建成功')
      router.push('/demands')
    } else {
      ElMessage.error(response.message || '创建失败')
    }
  } catch (error) {
    console.error('Failed to create demand:', error)
    ElMessage.error('创建失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadOptions()
})
</script>

<style scoped>
.create-demand {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.form-section {
  margin-bottom: 30px;
}

.form-section h3 {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.form-actions {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.form-actions .el-button {
  min-width: 120px;
  margin: 0 10px;
}
</style> 