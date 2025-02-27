<template>
  <div class="demand-detail">
    <div class="header">
      <h2>需求详情</h2>
      <el-button type="primary" @click="router.push(`/demands/${route.params.dingtalkNumber}/edit`)">
        编辑
      </el-button>
    </div>
    
    <el-descriptions
      v-if="demand"
      :column="3"
      border
    >
      <el-descriptions-item label="营销编号">{{ demand.marketing_number }}</el-descriptions-item>
      <el-descriptions-item label="钉钉号">{{ demand.dingtalk_number }}</el-descriptions-item>
      <el-descriptions-item label="ASIN">{{ demand.asin }}</el-descriptions-item>
      
      <el-descriptions-item label="评估数量">{{ demand.assessment_quantity }}</el-descriptions-item>
      <el-descriptions-item label="文字评论数">{{ demand.text_review_quantity }}</el-descriptions-item>
      <el-descriptions-item label="图片评论数">{{ demand.image_review_quantity }}</el-descriptions-item>
      
      <el-descriptions-item label="视频评论数">{{ demand.video_review_quantity }}</el-descriptions-item>
      <el-descriptions-item label="产品价格">{{ demand.product_price }}</el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="getStatusType(demand.status_id)">
          {{ getStatusText(demand.status_id) }}
        </el-tag>
      </el-descriptions-item>
      
      <el-descriptions-item label="搜索关键词" :span="3">{{ demand.search_keyword }}</el-descriptions-item>
      <el-descriptions-item label="链接" :span="3">
        <el-link type="primary" :href="demand.hyperlink" target="_blank">{{ demand.hyperlink }}</el-link>
      </el-descriptions-item>
      <el-descriptions-item label="备注" :span="3">{{ demand.other_notes }}</el-descriptions-item>
    </el-descriptions>

    <div v-else class="loading">
      <el-empty description="未找到需求数据" />
    </div>

    <!-- 添加统计信息展示 -->
    <el-card class="statistics-card" v-if="details.length > 0">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="statistic-item">
            <div class="label">总金额</div>
            <div class="value">¥{{ statistics.totalAmount.toFixed(2) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="statistic-item">
            <div class="label">完成率</div>
            <div class="value">{{ statistics.completionRate }}%</div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="statistic-item">
            <div class="label">状态分布</div>
            <div class="value">
              <el-tag size="small" style="margin-right: 8px">
                待评论: {{ statistics.statusCounts[1] }}
              </el-tag>
              <el-tag type="warning" size="small" style="margin-right: 8px">
                已评论: {{ statistics.statusCounts[2] }}
              </el-tag>
              <el-tag type="success" size="small">
                已完成: {{ statistics.statusCounts[3] }}
              </el-tag>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 添加测评明细列表 -->
    <div class="details-list">
      <el-card v-loading="loading">
        <template #header>
          <div class="card-header">
            <span>测评明细列表</span>
            <el-button type="primary" @click="$router.push(`/demands/${demandId}/details/create`)">
              新增明细
            </el-button>
          </div>
        </template>
        
        <el-table :data="details" style="width: 100%" v-loading="loading">
          <el-table-column prop="order_number" label="订单号" />
          <el-table-column prop="order_amount" label="订单金额">
            <template #default="{ row }">
              ¥{{ row.order_amount.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="order_time" label="下单时间" />
          <el-table-column label="订单截图">
            <template #default="{ row }">
              <el-image 
                v-if="row.order_screenshot"
                :src="getPreviewUrl(row.order_screenshot)"
                :preview-src-list="getPreviewList(row.order_screenshot)"
                fit="cover"
                style="width: 50px; height: 50px; cursor: pointer"
                preview-teleported
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
            </template>
          </el-table-column>
          <el-table-column label="评价截图">
            <template #default="{ row }">
              <el-image 
                v-if="row.review_screenshot"
                :src="getPreviewUrl(row.review_screenshot)"
                :preview-src-list="getPreviewList(row.review_screenshot)"
                fit="cover"
                style="width: 50px; height: 50px; cursor: pointer"
                preview-teleported
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
            </template>
          </el-table-column>
          <el-table-column label="支付截图">
            <template #default="{ row }">
              <el-image 
                v-if="row.payment_screenshot"
                :src="getPreviewUrl(row.payment_screenshot)"
                :preview-src-list="getPreviewList(row.payment_screenshot)"
                fit="cover"
                style="width: 50px; height: 50px; cursor: pointer"
                preview-teleported
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="agent_name" label="中介" width="120">
            <template #default="{ row }">
              <template v-if="row.agent_id">
                <el-tag size="small" type="success">
                  {{ row.agent_name }}
                </el-tag>
              </template>
              <template v-else>
                <el-tag size="small" type="info">未分配</el-tag>
              </template>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small" 
                @click="$router.push(`/demands/${demandId}/details/${row.detail_id}/edit`)"
              >
                编辑
              </el-button>
              
              <el-button 
                type="danger" 
                size="small" 
                @click="deleteDetail(row.detail_id)"
              >
                删除
              </el-button>
              
              <el-button 
                type="success" 
                size="small" 
                @click="showAssignAgentDialog(row)"
              >
                分配中介
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 添加中介和订单管理部分 -->
    <el-divider content-position="left">中介与订单管理</el-divider>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>中介分配与完成情况</span>
          <el-button type="primary" @click="showAgentDialog">添加中介</el-button>
        </div>
      </template>

      <el-table v-loading="agentsLoading" :data="agentList" stripe style="width: 100%">
        <el-table-column prop="agent_name" label="中介名称" />
        <el-table-column prop="contact_info" label="联系方式" />
        <el-table-column prop="target_count" label="目标数量">
          <template #default="{ row }">
            <el-input-number 
              v-model="row.target_count" 
              :min="0" 
              size="small"
              @change="updateTargetCount(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="actual_count" label="实际完成数量" />
        <el-table-column prop="completion_rate" label="完成率">
          <template #default="{ row }">
            <el-progress 
              :percentage="row.completion_rate" 
              :status="getProgressStatus(row.completion_rate)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="createOrderDetails(row)"
            >
              添加订单
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="removeAgent(row)"
            >
              移除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 无数据时显示 -->
      <el-empty v-if="agentList.length === 0" description="暂无中介分配" />
    </el-card>
    
    <!-- 添加中介弹窗 -->
    <el-dialog
      v-model="agentDialogVisible"
      title="添加中介"
      width="500px"
    >
      <el-form :model="agentForm" label-width="100px">
        <el-form-item label="选择中介">
          <el-select v-model="agentForm.agent_id" placeholder="请选择中介" style="width: 100%">
            <el-option
              v-for="agent in availableAgents"
              :key="agent.agent_id"
              :label="agent.agent_name"
              :value="agent.agent_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="目标数量">
          <el-input-number v-model="agentForm.target_count" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="agentDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="assignAgent" :loading="assignLoading">
            确认添加
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加订单弹窗 -->
    <el-dialog
      v-model="orderDialogVisible"
      title="添加订单"
      width="500px"
    >
      <el-form :model="orderForm" label-width="100px">
        <el-form-item label="订单号">
          <el-input v-model="orderForm.order_number" placeholder="请输入订单号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="orderDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createOrder" :loading="orderLoading">
            确认添加
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加分配中介的对话框 -->
    <el-dialog
      v-model="assignAgentDialogVisible"
      title="分配中介"
      width="500px"
    >
      <el-form :model="assignAgentForm" label-width="100px">
        <el-form-item label="测评明细">
          <div>订单号: {{ currentDetail?.order_number }}</div>
          <div>金额: {{ currentDetail?.order_amount }}</div>
        </el-form-item>
        
        <el-form-item label="选择中介">
          <el-select v-model="assignAgentForm.agent_id" placeholder="请选择中介" style="width: 100%">
            <el-option
              v-for="agent in availableAgents"
              :key="agent.agent_id"
              :label="agent.agent_name"
              :value="agent.agent_id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="assignAgentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="assignAgentToDetail" :loading="assignAgentLoading">
          确认分配
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/axios'
import { getDemandDetails } from '../../api/detail'
import type { DemandDetail } from '../../types/detail'
import { useDetailStore } from '../../stores/detail'

interface Demand {
  marketing_number: string
  dingtalk_number: string
  asin: string
  assessment_quantity: number
  text_review_quantity: number
  image_review_quantity: number
  video_review_quantity: number
  product_price: number
  search_keyword: string
  hyperlink: string
  other_notes: string
  status_id: number
  intermediary_name?: string
  intermediary_status?: number
  payment_status?: number
  assignment_time?: string
  completion_time?: string
  payment_amount?: number
  payment_time?: string
  intermediary_remark?: string
}

const route = useRoute()
const router = useRouter()
const demand = ref<Demand | null>(null)
const details = ref<DemandDetail[]>([])
const loading = ref(false)
const detailStore = useDetailStore()
const baseUrl = import.meta.env.VITE_API_URL
const demandId = computed(() => route.params.id)

// 新增中介和订单相关代码
const agentsLoading = ref(false)
const orderLoading = ref(false)
const agentList = ref<any[]>([])
const agentOrderDetails = ref<any[]>([])
const selectedAgent = ref<any>(null)
const availableAgents = ref<any[]>([])
const agentDialogVisible = ref(false)
const showOrderForm = ref(false)

const agentForm = ref({
  agent_id: '',
  target_count: 1
})

const orderForm = ref({
  order_number: '',
  demand_id: route.params.id,
  agent_id: ''
})

const assignAgentDialogVisible = ref(false)
const assignAgentForm = ref({
  agent_id: null,
  detail_id: null
})
const assignAgentLoading = ref(false)
const currentDetail = ref(null)

const loadDemand = async () => {
  try {
    if (!demandId.value) {
      ElMessage.error('需求ID不存在')
      return
    }
    const { data: response } = await request.get(`/api/demands/${demandId.value}`)
    if (response.code === 0) {
      demand.value = response.data
    } else {
      ElMessage.error(response.message || '加载失败')
    }
  } catch (error) {
    console.error('Failed to load demand:', error)
    ElMessage.error('加载失败')
  }
}

const loadDetails = async () => {
  try {
    loading.value = true
    const { data: response } = await request.get(`/api/demands/${demandId.value}/details`)
    if (response.code === 0) {
      details.value = response.data.map((detail: any) => {
        return {
          ...detail,
          status_text: getStatusText(detail.status)
        }
      })
    } else {
      ElMessage.error(response.message || '加载明细列表失败')
    }
  } catch (error) {
    console.error('Failed to load details:', error)
    ElMessage.error('加载明细列表失败')
  } finally {
    loading.value = false
  }
}

// 监听路由查询参数变化
watch(
  () => route.query,
  (query) => {
    if (query.refresh === 'true') {
      loadDetails()
    }
    if (query.newDetailId) {
      // 如果有新创建的明细ID，可以高亮显示或滚动到该明细
      const detailElement = document.getElementById(`detail-${query.newDetailId}`)
      if (detailElement) {
        detailElement.scrollIntoView({ behavior: 'smooth' })
        detailElement.classList.add('highlight')
      }
    }
  },
  { immediate: true }
)

const getStatusType = (status: number) => {
  const types: Record<number, '' | 'warning' | 'success'> = {
    1: '',        // 待评论
    2: 'warning', // 已评论
    3: 'success'  // 已完成
  }
  return types[status] || ''
}

const getStatusText = (status: number) => {
  const texts: Record<number, string> = {
    1: '待评论',
    2: '已评论',
    3: '已完成'
  }
  return texts[status] || '未知'
}

const getIntermediaryStatusType = (status: number) => {
  const types: Record<number, '' | 'warning' | 'danger' | 'success'> = {
    1: '',        // 未开始
    2: 'warning', // 进行中
    3: 'danger',  // 已取消
    4: 'success'  // 已完成
  }
  return types[status] || ''
}

const getIntermediaryStatusText = (status: number) => {
  const texts: Record<number, string> = {
    1: '未开始',
    2: '进行中',
    3: '已取消',
    4: '已完成'
  }
  return texts[status] || '未知'
}

const getPaymentStatusType = (status: number) => {
  const types: Record<number, '' | 'warning' | 'success'> = {
    1: '',        // 未支付
    2: 'warning', // 部分支付
    3: 'success'  // 已支付
  }
  return types[status] || ''
}

const getPaymentStatusText = (status: number) => {
  const texts: Record<number, string> = {
    1: '未支付',
    2: '部分支付',
    3: '已支付'
  }
  return texts[status] || '未知'
}

// 添加统计计算
const statistics = computed(() => {
  const totalAmount = details.value.reduce((sum, detail) => sum + Number(detail.order_amount || 0), 0)
  const completedCount = details.value.filter(d => d.status === 3).length
  const completionRate = details.value.length ? Math.round((completedCount / details.value.length) * 100) : 0
  
  const statusCounts = {
    1: details.value.filter(d => d.status === 1).length, // 待评论
    2: details.value.filter(d => d.status === 2).length, // 已评论
    3: completedCount // 已完成
  }
  
  return {
    totalAmount,
    completionRate,
    statusCounts
  }
})

// 添加图片预览相关的状态
const getPreviewUrl = (url: string | null) => {
  if (!url) return ''
  return baseUrl + url
}

const getPreviewList = (url: string | null) => {
  if (!url) return []
  return [baseUrl + url]
}

// 加载中介订单
const loadAgentOrders = async () => {
  try {
    agentsLoading.value = true
    const res = await request.get(`/api/demands/${route.params.id}/agents`)
    if (res.data && res.data.code === 0) {
      agentList.value = res.data.data || []
    } else {
      console.error('Failed to load agent orders:', res.data?.message)
      agentList.value = []
    }
  } catch (error) {
    console.error('Failed to load agent orders:', error)
    agentList.value = []
  } finally {
    agentsLoading.value = false
  }
}

// 显示中介弹窗
const showAgentDialog = async () => {
  agentDialogVisible.value = true
  agentForm.value = {
    agent_id: null,
    target_count: 1
  }
  await loadAvailableAgents()
}

// 加载可用中介
const loadAvailableAgents = async () => {
  try {
    const res = await request.get('/api/agents/available')
    if (res.data && res.data.code === 0) {
      availableAgents.value = res.data.data || []
    } else {
      console.error('Failed to load available agents:', res.data?.message)
      availableAgents.value = []
    }
  } catch (error) {
    console.error('Failed to load available agents:', error)
    availableAgents.value = []
  }
}

// 分配中介
const assignAgent = async () => {
  if (!agentForm.value.agent_id) {
    return ElMessage.warning('请选择中介')
  }
  
  try {
    assignLoading.value = true
    const res = await request.post(`/api/demands/${route.params.id}/agents`, agentForm.value)
    
    if (res.data && res.data.code === 0) {
      ElMessage.success('中介分配成功')
      agentDialogVisible.value = false
      loadAgentOrders()
    } else {
      ElMessage.error(res.data?.message || '分配失败')
    }
  } catch (error) {
    console.error('Failed to assign agent:', error)
    ElMessage.error('分配失败')
  } finally {
    assignLoading.value = false
  }
}

// 处理添加订单
const createOrderDetails = (agent: any) => {
  selectedAgent.value = agent
  orderForm.value.agent_id = agent.agent_id
  showOrderForm.value = true
  loadAgentOrderDetails(agent.agent_id)
}

// 提交订单表单
const createOrder = async () => {
  try {
    if (!orderForm.value.order_number) {
      return ElMessage.warning('请输入订单号')
    }
    
    const res = await request.post('/api/orders', orderForm.value)
    
    if (res.data.code === 0) {
      ElMessage.success('添加订单成功')
      showOrderForm.value = false
      loadAgentOrderDetails(selectedAgent.value.agent_id)
      loadAgentOrders() // 更新完成率
    } else {
      ElMessage.error(res.data.message || '添加失败')
    }
  } catch (error: any) {
    console.error('Failed to add order:', error)
    ElMessage.error(error.response?.data?.message || '添加失败')
  }
}

// 处理移除中介
const removeAgent = (agent: any) => {
  ElMessageBox.confirm(
    '确定要移除该中介吗？关联的订单将一并删除。',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await request.delete(`/api/demands/${route.params.id}/agents/${agent.agent_id}`)
      
      if (res.data.code === 0) {
        ElMessage.success('移除中介成功')
        loadAgentOrders()
        if (selectedAgent.value?.agent_id === agent.agent_id) {
          selectedAgent.value = null
        }
      } else {
        ElMessage.error(res.data.message || '移除失败')
      }
    } catch (error: any) {
      console.error('Failed to remove agent:', error)
      ElMessage.error(error.response?.data?.message || '移除失败')
    }
  }).catch(() => {
    // 取消操作
  })
}

// 更新目标数量
const updateTargetCount = async (agent: any) => {
  try {
    const res = await request.put(`/api/orders/${agent.order_id}`, {
      target_count: agent.target_count
    })
    
    if (res.data.code === 0) {
      ElMessage.success('更新目标数量成功')
    } else {
      ElMessage.error(res.data.message || '更新失败')
    }
  } catch (error: any) {
    console.error('Failed to update target count:', error)
    ElMessage.error(error.response?.data?.message || '更新失败')
  }
}

// 加载中介的订单详情
const loadAgentOrderDetails = async (agentId: number) => {
  try {
    orderLoading.value = true
    const res = await request.get(`/api/demands/${route.params.id}/agents/${agentId}/orders`)
    agentOrderDetails.value = res.data.data.map((order: any) => ({
      ...order,
      status_text: order.status === 1 ? '进行中' : order.status === 2 ? '已完成' : '已取消'
    }))
  } catch (error) {
    console.error('Failed to load agent order details:', error)
    ElMessage.error('加载中介订单详情失败')
  } finally {
    orderLoading.value = false
  }
}

// 计算完成率状态
const getProgressStatus = (rate: number) => {
  if (rate >= 100) return 'success'
  if (rate >= 50) return 'warning'
  return 'exception'
}

// 显示分配中介弹窗
const showAssignAgentDialog = async (detail) => {
  currentDetail.value = detail
  assignAgentForm.value = {
    agent_id: detail.agent_id || null,
    detail_id: detail.detail_id
  }
  assignAgentDialogVisible.value = true
  
  try {
    // 加载所有可用中介（使用修改后的API函数名）
    const res = await request.get('/api/agents/available')
    console.log('获取到的中介数据:', res.data)
    if (res.data && res.data.code === 0) {
      availableAgents.value = res.data.data || []
    } else {
      // 如果获取关联中介失败，尝试获取所有中介
      const fallbackRes = await request.get('/api/intermediaries')
      availableAgents.value = fallbackRes.data || []
      if (availableAgents.value.length === 0) {
        ElMessage.warning('没有可用的中介')
      }
    }
  } catch (error) {
    console.error('Failed to load agents:', error)
    ElMessage.error('加载中介列表失败')
  }
}

// 分配中介给明细
const assignAgentToDetail = async () => {
  if (!assignAgentForm.value.agent_id) {
    return ElMessage.warning('请选择中介')
  }
  
  const apiUrl = `/api/detail-agent-assign/${assignAgentForm.value.detail_id}`
  const requestData = {
    agent_id: assignAgentForm.value.agent_id
  }
  
  console.log('准备发送请求:', { url: apiUrl, data: requestData })
  
  try {
    assignAgentLoading.value = true
    
    const res = await request.post(apiUrl, requestData)
    console.log('分配中介响应:', res)
    
    if (res.data && res.data.code === 0) {
      ElMessage.success('分配中介成功')
      assignAgentDialogVisible.value = false
      // 重新加载明细列表
      loadDetails()
    } else {
      ElMessage.error(res.data?.message || '分配失败')
    }
  } catch (error) {
    console.error('Failed to assign agent to detail:', error)
    ElMessage.error('分配失败: ' + (error.message || '未知错误'))
  } finally {
    assignAgentLoading.value = false
  }
}

onMounted(() => {
  loadDemand()
  loadDetails()
  loadAgentOrders()
})
</script>

<style scoped>
.demand-detail {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.loading {
  padding: 40px;
  text-align: center;
}

.details-list {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.statistics-card {
  margin: 20px 0;
}

.statistic-item {
  text-align: center;
  padding: 16px;
}

.statistic-item .label {
  color: var(--el-text-color-secondary);
  font-size: 14px;
  margin-bottom: 8px;
}

.statistic-item .value {
  font-size: 24px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.highlight {
  animation: highlight 2s ease-out;
}

@keyframes highlight {
  0% {
    background-color: var(--el-color-primary-light-8);
  }
  100% {
    background-color: transparent;
  }
}

.image-error {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 50px;
  height: 50px;
  background-color: var(--el-fill-color-light);
  color: var(--el-text-color-secondary);
}

.el-image {
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter);
  transition: all 0.3s;
  background-color: var(--el-fill-color-lighter);
}

.el-image:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 添加图片加载时的占位样式 */
.el-image :deep(.el-image__placeholder) {
  background-color: var(--el-fill-color-lighter);
  display: flex;
  align-items: center;
  justify-content: center;
}

.el-image :deep(.el-image__error) {
  background-color: var(--el-fill-color-lighter);
}
</style> 