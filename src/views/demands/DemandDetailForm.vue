<template>
  <div class="detail-form-container">
    <div class="form-header">
      <h2>{{ detailId ? '编辑' : '新增' }}测评明细</h2>
      <div>
        <el-button @click="testLoadAgents" :loading="testLoading">测试加载中介</el-button>
        <el-button @click="router.push(`/demands/${demandId}`)">返回</el-button>
        <el-button type="primary" @click="saveDetail" :loading="loading">保存</el-button>
      </div>
    </div>

    <el-form 
      ref="formRef" 
      :model="form" 
      :rules="rules" 
      label-width="100px" 
      class="detail-form"
      v-loading="loading"
    >
      <!-- 订单信息部分 -->
      <el-divider content-position="left">订单信息</el-divider>
      
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
              style="width: 100%"
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
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="订单状态" prop="status">
            <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
              <el-option :value="1" label="待评论" />
              <el-option :value="2" label="已评论" />
              <el-option :value="3" label="已完成" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 中介分配部分 -->
      <el-divider content-position="left">中介分配</el-divider>
      
      <el-form-item label="分配中介">
        <el-select v-model="form.agent_id" clearable placeholder="选择中介(可选)" style="width: 100%">
          <el-option
            v-for="agent in availableAgents"
            :key="agent.agent_id"
            :label="agent.agent_name"
            :value="agent.agent_id"
          />
        </el-select>
        <div class="form-help" v-if="form.agent_id">
          当前选择: <el-tag>{{ getAgentName(form.agent_id) }}</el-tag>
        </div>
      </el-form-item>
      
      <!-- 评价内容部分 -->
      <el-divider content-position="left">评价内容</el-divider>
      
      <el-form-item label="评价内容" prop="review_content">
        <el-input 
          v-model="form.review_content" 
          type="textarea" 
          rows="4"
          placeholder="请输入评价内容"
        />
      </el-form-item>
      
      <el-form-item label="评价时间" prop="review_time">
        <el-date-picker 
          v-model="form.review_time" 
          type="datetime" 
          placeholder="选择评价时间" 
          style="width: 100%"
        />
      </el-form-item>
      
      <!-- 图片上传部分 -->
      <el-divider content-position="left">相关截图</el-divider>
      
      <el-form-item label="订单截图">
        <el-upload
          action="/api/upload"
          :on-success="handleOrderScreenshotSuccess"
          :on-error="handleUploadError"
          :file-list="orderScreenshotList"
        >
          <el-button type="primary">上传订单截图</el-button>
        </el-upload>
      </el-form-item>
      
      <el-form-item label="支付截图">
        <el-upload
          action="/api/upload"
          :on-success="handlePaymentScreenshotSuccess"
          :on-error="handleUploadError"
          :file-list="paymentScreenshotList"
        >
          <el-button type="primary">上传支付截图</el-button>
        </el-upload>
      </el-form-item>
      
      <el-form-item label="评价截图">
        <el-upload
          action="/api/upload"
          :on-success="handleReviewScreenshotSuccess"
          :on-error="handleUploadError"
          :file-list="reviewScreenshotList"
        >
          <el-button type="primary">上传评价截图</el-button>
        </el-upload>
      </el-form-item>
      
      <el-form-item label="备注" prop="remark">
        <el-input 
          v-model="form.remark" 
          type="textarea" 
          rows="3"
          placeholder="请输入备注信息(可选)"
        />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/axios'

const route = useRoute()
const router = useRouter()
const demandId = route.params.id
const detailId = route.params.detailId
const loading = ref(false)
const testLoading = ref(false)

// 表单数据
const form = ref({
  order_number: '',
  order_amount: 0,
  order_time: '',
  review_content: '',
  review_time: '',
  review_images: [],
  review_video: '',
  payment_screenshot: '',
  order_screenshot: '',
  review_screenshot: '',
  status: 1,
  remark: '',
  agent_id: null  // 添加中介ID字段
})

// 上传文件列表
const orderScreenshotList = ref([])
const paymentScreenshotList = ref([])
const reviewScreenshotList = ref([])

// 可用中介列表
const availableAgents = ref([])

// 表单规则
const rules = reactive({
  order_number: [{ required: true, message: '请输入订单号', trigger: 'blur' }],
  order_amount: [{ required: true, message: '请输入订单金额', trigger: 'change' }],
  order_time: [{ required: true, message: '请选择下单时间', trigger: 'change' }]
})

// 获取中介名称
const getAgentName = (id) => {
  const agent = availableAgents.value.find(a => a.agent_id === id)
  return agent ? agent.agent_name : '未知中介'
}

// 加载可用的中介
const loadAvailableAgents = async () => {
  try {
    console.log('开始加载中介数据...')
    
    // 1. 首先尝试获取accounts中的中介数据
    const accountRes = await request.get('/api/accounts/intermediaries')
    console.log('从accounts获取的中介数据:', accountRes.data)
    
    if (accountRes.data && accountRes.data.code === 0 && accountRes.data.data.length > 0) {
      // 确保字段匹配：如果accounts表中的字段名不同，进行映射
      availableAgents.value = accountRes.data.data.map(item => ({
        agent_id: item.account_id || item.id,
        agent_name: item.account_name || item.name,
        contact_info: item.contact_info || item.contact
      }))
      console.log('映射后的中介列表:', availableAgents.value)
      return  // 如果成功获取，直接返回
    }
    
    // 2. 如果第一种方法失败，尝试获取需求关联的中介
    try {
      const res = await request.get(`/api/demands/${demandId}/available-agents`)
      console.log('获取到需求关联中介数据:', res.data)
      
      if (res.data && res.data.code === 0 && res.data.data.length > 0) {
        availableAgents.value = res.data.data
        return
      }
    } catch (err) {
      console.error('获取需求关联中介失败:', err)
    }
    
    // 3. 尝试获取所有可用中介
    try {
      const allRes = await request.get('/api/agents/available')
      console.log('获取所有可用中介:', allRes.data)
      
      if (allRes.data && allRes.data.code === 0) {
        availableAgents.value = allRes.data.data || []
        return
      }
    } catch (err) {
      console.error('获取所有可用中介失败:', err)
    }
    
    // 4. 最后的备用方案
    try {
      const fallbackRes = await request.get('/api/intermediaries')
      console.log('备用API获取中介:', fallbackRes.data)
      
      if (fallbackRes.data && fallbackRes.data.length > 0) {
        availableAgents.value = fallbackRes.data
        return
      }
    } catch (err) {
      console.error('备用API获取中介失败:', err)
    }
    
    // 5. 如果所有方法都失败，尝试直接从accounts表获取所有账户
    try {
      const accountsRes = await request.get('/api/accounts')
      console.log('获取所有账户:', accountsRes.data)
      
      if (accountsRes.data && accountsRes.data.code === 0) {
        // 过滤出中介类型的账户，并映射字段
        availableAgents.value = accountsRes.data.data
          .filter(account => account.role === 'intermediary' || account.type === 'intermediary')
          .map(account => ({
            agent_id: account.id || account.account_id,
            agent_name: account.name || account.account_name || account.username,
            contact_info: account.contact || account.contact_info || account.phone
          }))
        return
      }
    } catch (err) {
      console.error('获取所有账户失败:', err)
    }
    
    console.log('所有方法都失败，中介列表为空')
    // 如果都失败了，显示空列表
    availableAgents.value = []
  } catch (error) {
    console.error('加载中介列表失败:', error)
    ElMessage.error('加载中介列表失败')
    availableAgents.value = []
  }
}

// 加载明细详情（编辑模式）
const loadDetail = async () => {
  if (!detailId) return
  
  try {
    loading.value = true
    const res = await request.get(`/api/demand-details/${detailId}`)
    console.log('加载明细详情响应:', res.data)
    
    if (res.data && res.data.code === 0) {
      const detail = res.data.data
      
      // 填充表单数据，包括中介ID
      form.value = {
        ...form.value,
        ...detail,
        agent_id: detail.agent_id || null
      }
      
      // 设置文件列表
      if (detail.order_screenshot) {
        orderScreenshotList.value = [{
          name: '订单截图',
          url: detail.order_screenshot
        }]
      }
      
      if (detail.payment_screenshot) {
        paymentScreenshotList.value = [{
          name: '支付截图',
          url: detail.payment_screenshot
        }]
      }
      
      if (detail.review_screenshot) {
        reviewScreenshotList.value = [{
          name: '评价截图',
          url: detail.review_screenshot
        }]
      }
      
      console.log('Loaded detail with agent:', detail.agent_id, detail.agent_name)
    } else {
      ElMessage.error(res.data?.message || '加载详情失败')
    }
  } catch (error) {
    console.error('Failed to load detail:', error)
    ElMessage.error('加载详情失败')
  } finally {
    loading.value = false
  }
}

// 上传成功处理函数
const handleOrderScreenshotSuccess = (response) => {
  if (response && response.code === 0) {
    form.value.order_screenshot = response.data.url
    ElMessage.success('订单截图上传成功')
  } else {
    ElMessage.error('上传失败')
  }
}

const handlePaymentScreenshotSuccess = (response) => {
  if (response && response.code === 0) {
    form.value.payment_screenshot = response.data.url
    ElMessage.success('支付截图上传成功')
  } else {
    ElMessage.error('上传失败')
  }
}

const handleReviewScreenshotSuccess = (response) => {
  if (response && response.code === 0) {
    form.value.review_screenshot = response.data.url
    ElMessage.success('评价截图上传成功')
  } else {
    ElMessage.error('上传失败')
  }
}

const handleUploadError = () => {
  ElMessage.error('上传失败')
}

// 保存表单
const saveDetail = async () => {
  try {
    loading.value = true
    const isEdit = !!detailId
    
    const formData = { ...form.value }
    console.log('准备提交表单数据:', formData)
    
    // 根据是否是编辑模式调用不同的API
    let res
    if (isEdit) {
      // 编辑已有明细 - 使用POST而不是PUT (因为后端已改为POST)
      res = await request.post(`/api/demand-details/${detailId}`, formData)
    } else {
      // 创建新明细
      res = await request.post(`/api/demands/${demandId}/details`, formData)
    }
    
    console.log('API响应:', res.data)
    
    if (res.data && res.data.code === 0) {
      ElMessage.success(isEdit ? '更新成功' : '创建成功')
      router.push(`/demands/${demandId}`)
    } else {
      ElMessage.error(res.data?.message || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 添加测试方法
const testLoadAgents = async () => {
  testLoading.value = true
  try {
    // 测试所有可能的API路径
    const apiPaths = [
      '/api/accounts/intermediaries',
      `/api/demands/${demandId}/available-agents`,
      '/api/agents/available',
      '/api/intermediaries',
      '/api/accounts'
    ]
    
    let success = false
    
    for (const path of apiPaths) {
      try {
        console.log(`尝试API: ${path}`)
        const res = await request.get(path)
        console.log(`API ${path} 响应:`, res.data)
        
        if (res.data && (res.data.code === 0 || Array.isArray(res.data))) {
          const data = res.data.data || res.data
          if (data && data.length > 0) {
            ElMessage.success(`成功从 ${path} 获取到 ${data.length} 个中介`)
            success = true
            break
          } else {
            console.log(`${path} 返回空数据`)
          }
        }
      } catch (err) {
        console.error(`API ${path} 失败:`, err)
      }
    }
    
    if (!success) {
      ElMessage.error('所有API尝试都失败，请检查后端')
    }
  } catch (error) {
    console.error('测试加载中介失败:', error)
    ElMessage.error('测试失败')
  } finally {
    testLoading.value = false
  }
}

// 添加API测试方法
const testAPIs = async () => {
  testLoading.value = true
  try {
    // 测试API
    const testAPIs = [
      { method: 'get', url: '/api/test' },
      { method: 'get', url: '/api/check-apis' },
      { method: 'get', url: '/api/accounts/intermediaries' },
      { method: 'get', url: `/api/demands/${demandId}/available-agents` }
    ]
    
    for (const api of testAPIs) {
      try {
        console.log(`测试 ${api.method.toUpperCase()} ${api.url}...`)
        const res = await request[api.method](api.url)
        console.log(`${api.url} 响应:`, res.data)
      } catch (err) {
        console.error(`${api.url} 失败:`, err)
      }
    }
    
    ElMessage.success('API测试完成，请查看控制台')
  } catch (error) {
    console.error('API测试失败:', error)
    ElMessage.error('测试失败')
  } finally {
    testLoading.value = false
  }
}

onMounted(() => {
  console.log('组件挂载 - 开始加载数据')
  // 加载中介数据
  loadAvailableAgents()
  
  // 如果是编辑模式，加载明细数据
  if (detailId) {
    loadDetail()
  }
})
</script>

<style scoped>
.detail-form-container {
  padding: 20px;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-form {
  max-width: 900px;
  margin: 0 auto;
}

.form-help {
  font-size: 12px;
  margin-top: 5px;
  color: #999;
}
</style> 