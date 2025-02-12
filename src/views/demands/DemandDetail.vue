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
    
    <el-divider content-position="left">中介信息</el-divider>
    
    <el-descriptions v-if="demand" :column="3" border>
      <el-descriptions-item label="分配中介">
        {{ demand.intermediary_name || '未分配' }}
      </el-descriptions-item>
      <el-descriptions-item label="中介状态">
        <el-tag :type="getIntermediaryStatusType(demand.intermediary_status)">
          {{ getIntermediaryStatusText(demand.intermediary_status) }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="支付状态">
        <el-tag :type="getPaymentStatusType(demand.payment_status)">
          {{ getPaymentStatusText(demand.payment_status) }}
        </el-tag>
      </el-descriptions-item>
      
      <el-descriptions-item label="分配时间">
        {{ demand.assignment_time || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="完成时间">
        {{ demand.completion_time || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="支付时间">
        {{ demand.payment_time || '-' }}
      </el-descriptions-item>
      
      <el-descriptions-item label="支付金额">
        {{ demand.payment_amount ? `¥${demand.payment_amount}` : '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="中介备注" :span="2">
        {{ demand.intermediary_remark || '-' }}
      </el-descriptions-item>
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
        
        <el-table :data="details" style="width: 100%">
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
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button-group>
                <el-button
                  type="primary"
                  link
                  @click="router.push(`/demands/${demandId}/details/${row.detail_id}`)"
                >
                  查看
                </el-button>
                <el-button
                  type="primary"
                  link
                  @click="router.push(`/demands/${demandId}/details/${row.detail_id}/edit`)"
                >
                  编辑
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
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

const loadDemand = async () => {
  try {
    if (!demandId.value) {
      ElMessage.error('需求ID不存在')
      return
    }
    const { data: response } = await axios.get(`/api/demands/${demandId.value}`)
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
  if (!demandId.value) {
    ElMessage.error('需求ID不存在')
    return
  }

  try {
    loading.value = true
    const { data: response } = await axios.get(`/api/demands/${demandId.value}/details`)
    if (response.code === 0) {
      details.value = response.data.map((detail: any) => ({
        ...detail,
        order_amount: Number(detail.order_amount)
      }))
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

onMounted(() => {
  loadDemand()
  loadDetails()
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