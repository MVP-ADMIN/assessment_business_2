<template>
  <div class="refund-list">
    <div class="header">
      <h2>返款管理</h2>
      <div class="actions">
        <el-button type="primary" @click="router.push('/refunds/create-payment')">
          创建返款
        </el-button>
      </div>
    </div>

    <!-- 调试信息 -->
    <el-card v-if="debug" class="debug-card">
      <h3>调试信息</h3>
      <div>Loading: {{ loading }}</div>
      <div>Data Count: {{ tableData.length }}</div>
      <pre>{{ JSON.stringify(tableData, null, 2) }}</pre>
    </el-card>

    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>返款列表</span>
          <el-button type="primary" link @click="loadData">刷新</el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        border
        style="width: 100%"
        row-key="id"
      >
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="order_number" label="订单号" min-width="120" show-overflow-tooltip />
        <el-table-column prop="marketing_number" label="营销编号" min-width="120" show-overflow-tooltip />
        <el-table-column prop="customer_email" label="客户邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column label="订单金额" min-width="120" align="right">
          <template #default="{ row }">
            {{ row.currency }} {{ formatAmount(row.order_amount) }}
          </template>
        </el-table-column>
        <el-table-column label="转账金额" min-width="120" align="right">
          <template #default="{ row }">
            {{ row.currency }} {{ formatAmount(row.transfer_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" min-width="100" />
        <el-table-column prop="payment_time" label="支付时间" min-width="160" />
        <el-table-column label="状态" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button 
              link 
              type="primary" 
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button 
              link 
              type="danger" 
              @click="handleDelete(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && tableData.length === 0" class="empty-data">
        暂无数据
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from '@/utils/axios'
import { refundApi } from '@/api/refund'

interface RefundRecord {
  id: number
  order_number: string
  marketing_number: string
  customer_email: string
  order_amount: string | number
  transfer_amount: string | number
  currency: string
  payment_method: string
  payment_time: string
  status: string
  payment_screenshot: string
}

const router = useRouter()
const loading = ref(false)
const tableData = ref<RefundRecord[]>([])
const debug = ref(true) // 开启调试模式

// 格式化金额
const formatAmount = (amount: string | number | null | undefined) => {
  if (amount === null || amount === undefined) return '-'
  return Number(amount).toFixed(2)
}

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'warning',
    processing: 'info',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '已失败'
  }
  return texts[status] || status
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    console.log('开始加载数据...')
    
    const { data: res } = await axios.get('/api/refunds/recent')
    console.log('API返回数据:', res)
    
    if (res.code === 0 && Array.isArray(res.data)) {
      tableData.value = res.data.map((item: RefundRecord) => ({
        ...item,
        order_amount: Number(item.order_amount),
        transfer_amount: Number(item.transfer_amount)
      }))
      console.log('处理后的表格数据:', tableData.value)
    } else {
      ElMessage.error(res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载数据出错:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleView = (row: any) => {
  router.push(`/refunds/${row.id}`)
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条返款记录吗？', '提示', {
      type: 'warning'
    })
    await refundApi.delete(id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete refund:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  console.log('组件挂载，开始加载数据')
  loadData()
})
</script>

<style scoped>
.refund-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-card {
  margin-bottom: 20px;
}

.debug-card {
  margin-bottom: 20px;
  background-color: #f8f9fa;
}

.debug-card pre {
  background: #fff;
  padding: 10px;
  border-radius: 4px;
  max-height: 300px;
  overflow: auto;
}

.empty-data {
  text-align: center;
  padding: 30px;
  color: #909399;
}

:deep(.el-table) {
  margin-top: 20px;
}
</style> 