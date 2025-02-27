<template>
  <div class="refund-list">
    <div class="header">
      <h2>返款管理</h2>
      <div class="actions">
        <el-button type="primary" @click="$router.push('/refunds/create')">
          新建返款
        </el-button>
      </div>
    </div>

    <el-card>
      <!-- 搜索表单 -->
      <el-form :model="searchForm" inline>
        <el-form-item label="订单号">
          <el-input v-model="searchForm.order_number" placeholder="请输入订单号" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态">
            <el-option label="待支付" value="pending" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="filteredData" border v-loading="loading">
        <el-table-column prop="order_number" label="订单号" />
        <el-table-column prop="marketing_number" label="营销编号" />
        <el-table-column prop="dingtalk_number" label="钉钉号" />
        <el-table-column label="订单金额">
          <template #default="{ row }">
            {{ row.order_amount }} {{ row.currency }}
          </template>
        </el-table-column>
        <el-table-column label="转账金额">
          <template #default="{ row }">
            {{ row.transfer_amount }} {{ row.currency }}
          </template>
        </el-table-column>
        <el-table-column prop="customer_email" label="客户邮箱" />
        <el-table-column prop="payment_method" label="支付方式" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order_date" label="订单时间" />
        <el-table-column prop="payment_time" label="支付时间" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button 
              link 
              type="primary" 
              @click="$router.push(`/refunds/${row.id}`)"
            >
              查看
            </el-button>
            <el-button 
              link 
              type="primary"
              v-if="row.status === 'pending'"
              @click="handleCreatePayment(row)"
            >
              支付
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { refundApi } from '@/api/refund'

const router = useRouter()
const loading = ref(false)
const tableData = ref<any[]>([])

const searchForm = ref({
  order_number: '',
  status: ''
})

// 过滤后的数据
const filteredData = computed(() => {
  let data = [...tableData.value]
  
  if (searchForm.value.order_number) {
    data = data.filter(item => 
      item.order_number.includes(searchForm.value.order_number)
    )
  }
  
  if (searchForm.value.status) {
    data = data.filter(item => 
      item.status === searchForm.value.status
    )
  }
  
  return data
})

// 获取列表数据
const fetchData = async () => {
  try {
    loading.value = true
    const res = await refundApi.list()
    
    if (res.code === 0) {
      tableData.value = res.data
    } else {
      throw new Error(res.message)
    }
  } catch (error: any) {
    console.error('Failed to fetch refunds:', error)
    ElMessage.error(error.message || '获取数据失败')
  } finally {
    loading.value = false
  }
}

// 获取状态样式
const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: '',        // 待支付
    completed: 'success' // 已完成
  }
  return types[status] || ''
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待支付',
    completed: '已完成'
  }
  return texts[status] || status
}

// 创建支付记录
const handleCreatePayment = (row: any) => {
  router.push(`/refunds/${row.id}/payments/create`)
}

// 搜索
const handleSearch = () => {
  // 使用计算属性，无需重新请求
}

// 重置搜索
const handleReset = () => {
  searchForm.value = {
    order_number: '',
    status: ''
  }
}

// 初始化
fetchData()
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
</style> 