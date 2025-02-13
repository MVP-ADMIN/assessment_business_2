<template>
  <div class="demands-page">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline @submit.prevent="handleSearch">
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索营销编号/钉钉号/ASIN"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="创建日期">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            unlink-panels
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" clearable placeholder="请选择状态">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            搜索
          </el-button>
          <el-button @click="resetSearch">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="left">
            <span class="title">需求列表</span>
            <el-tag type="info" class="count">
              共 {{ total }} 条
            </el-tag>
          </div>
          <div class="right">
            <el-button type="primary" @click="$router.push('/demands/create')">
              创建需求
            </el-button>
            <el-button @click="handleExport">
              导出
            </el-button>
          </div>
        </div>
      </template>

      <el-table 
        :data="tableData" 
        v-loading="loading" 
        border
        style="width: 100%"
      >
        <el-table-column prop="marketing_number" label="营销编号" min-width="120" />
        <el-table-column prop="dingtalk_number" label="钉钉号" min-width="120" />
        <el-table-column prop="asin" label="ASIN" min-width="120" />
        <el-table-column prop="assessment_quantity" label="评估数量" width="100" />
        <el-table-column label="评论数量" width="280">
          <template #default="{ row }">
            <el-space>
              <el-tag size="small">文字: {{ row.text_review_quantity }}</el-tag>
              <el-tag size="small" type="success">图片: {{ row.image_review_quantity }}</el-tag>
              <el-tag size="small" type="warning">视频: {{ row.video_review_quantity }}</el-tag>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column prop="status_name" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status_id)">
              {{ row.status_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button 
              link 
              type="primary" 
              @click="$router.push(`/demands/${row.demand_id}`)"
            >
              查看
            </el-button>
            <el-button 
              link 
              type="primary" 
              @click="$router.push(`/demands/${row.demand_id}/edit`)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.status_id === 1"
              link
              type="warning"
              @click="handlePause(row)"
            >
              暂停
            </el-button>
            <el-button
              v-if="row.status_id === 2"
              link
              type="success"
              @click="handleResume(row)"
            >
              恢复
            </el-button>
            <el-button 
              v-if="[1, 2].includes(row.status_id)"
              link
              type="danger"
              @click="handleStop(row)"
            >
              终止
            </el-button>
            <el-button 
              link
              type="primary"
              @click="handleHistory(row)"
            >
              变更记录
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 状态变更原因对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form
        ref="reasonFormRef"
        :model="reasonForm"
        :rules="reasonRules"
        label-width="80px"
      >
        <el-form-item label="原因" prop="reason">
          <el-input
            v-model="reasonForm.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入变更原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 变更历史对话框 -->
    <el-dialog
      v-model="historyVisible"
      title="状态变更历史"
      width="680px"
      destroy-on-close
    >
      <div v-if="historyList && historyList.length > 0" class="history-timeline">
        <el-timeline>
          <el-timeline-item
            v-for="item in historyList"
            :key="item.log_id"
            :timestamp="item.change_time"
            :type="getHistoryItemType(item)"
          >
            <h4>{{ item.change_description }}</h4>
            <p class="status-change">
              状态变更: 
              <el-tag size="small" :type="getStatusType(item.old_status_id)">
                {{ item.old_status_name }}
              </el-tag>
              <el-icon class="mx-2"><ArrowRight /></el-icon>
              <el-tag size="small" :type="getStatusType(item.new_status_id)">
                {{ item.new_status_name }}
              </el-tag>
            </p>
          </el-timeline-item>
        </el-timeline>
      </div>
      <div v-else class="no-history">
        暂无变更记录
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { demandApi } from '@/api/demand'
import type { Demand } from '@/types/demand'
import { DemandStatus } from '@/types/demand'

const loading = ref(false)
const tableData = ref<Demand[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const searchForm = ref({
  keyword: '',
  dateRange: [],
  status: ''
})

const statusOptions = [
  { value: 1, label: '进行中' },
  { value: 2, label: '已暂停' },
  { value: 3, label: '已终止' }
]

// 状态变更相关
const dialogVisible = ref(false)
const dialogTitle = ref('')
const currentAction = ref<'pause' | 'resume' | 'stop'>('pause')
const currentDemand = ref<any>(null)
const reasonFormRef = ref()
const reasonForm = ref({
  reason: ''
})

const reasonRules = {
  reason: [
    { required: true, message: '请输入变更原因', trigger: 'blur' }
  ]
}

// 添加变更历史相关的状态
const historyVisible = ref(false)
const historyList = ref<any[]>([])

// 获取数据
const loadData = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      keyword: searchForm.value.keyword,
      status: searchForm.value.status,
      start_date: searchForm.value.dateRange[0],
      end_date: searchForm.value.dateRange[1]
    }
    const { list, total: totalCount } = await demandApi.list(params)
    tableData.value = list
    total.value = totalCount
  } catch (error) {
    console.error('Failed to load demands:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    keyword: '',
    dateRange: [],
    status: ''
  }
  currentPage.value = 1
  loadData()
}

// 删除
const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条需求吗？', '提示', {
      type: 'warning'
    })
    await demandApi.delete(id)
    ElMessage.success('删除成功')
    if (tableData.value.length === 1 && currentPage.value > 1) {
      currentPage.value--
    }
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete demand:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 导出
const handleExport = async () => {
  try {
    const params = {
      keyword: searchForm.value.keyword,
      status: searchForm.value.status,
      start_date: searchForm.value.dateRange[0],
      end_date: searchForm.value.dateRange[1]
    }
    const blob = await demandApi.export(params)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `需求列表_${new Date().toLocaleDateString()}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export demands:', error)
    ElMessage.error('导出失败')
  }
}

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadData()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadData()
}

// 暂停需求
const handlePause = async (row: any) => {
  try {
    currentDemand.value = row
    currentAction.value = 'pause'
    dialogTitle.value = '暂停需求'
    reasonForm.value.reason = ''
    dialogVisible.value = true
  } catch (error) {
    console.error('Failed to pause demand:', error)
    ElMessage.error('操作失败')
  }
}

// 恢复需求
const handleResume = async (row: any) => {
  try {
    currentDemand.value = row
    currentAction.value = 'resume'
    dialogTitle.value = '恢复需求'
    reasonForm.value.reason = ''
    dialogVisible.value = true
  } catch (error) {
    console.error('Failed to resume demand:', error)
    ElMessage.error('操作失败')
  }
}

// 终止需求
const handleStop = async (row: any) => {
  try {
    currentDemand.value = row
    currentAction.value = 'stop'
    dialogTitle.value = '终止需求'
    reasonForm.value.reason = ''
    dialogVisible.value = true
  } catch (error) {
    console.error('Failed to stop demand:', error)
    ElMessage.error('操作失败')
  }
}

// 确认状态变更
const handleConfirm = async () => {
  if (!reasonFormRef.value) return
  
  try {
    await reasonFormRef.value.validate()
    const { reason } = reasonForm.value
    const id = currentDemand.value.demand_id
    
    // 根据不同action调用不同API
    const api = {
      pause: demandApi.pause,
      resume: demandApi.resume,
      stop: demandApi.stop
    }[currentAction.value]
    
    await api(id, { reason })
    ElMessage.success('操作成功')
    dialogVisible.value = false
    loadData() // 重新加载数据
  } catch (error) {
    console.error('Failed to confirm action:', error)
    ElMessage.error('操作失败')
  }
}

// 获取状态类型
const getStatusType = (statusId: number) => {
  const types: Record<number, '' | 'success' | 'warning' | 'danger'> = {
    1: 'warning',  // 进行中
    2: 'info',     // 已暂停
    3: 'danger'    // 已终止
  }
  return types[statusId] || ''
}

// 查看变更历史
const handleHistory = async (row: any) => {
  try {
    historyVisible.value = true
    const response = await demandApi.getHistory(row.demand_id)
    console.log('History response:', response)
    
    if (response.code === 0) {
      // 直接使用返回的数据，只格式化时间
      historyList.value = response.data.map(item => ({
        ...item,
        change_time: new Date(item.change_time).toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        })
      }))
      console.log('Processed history:', historyList.value)
    } else {
      historyList.value = []
      ElMessage.warning('没有找到变更记录')
    }
  } catch (error) {
    console.error('Failed to load history:', error)
    ElMessage.error('加载历史记录失败')
  }
}

// 获取历史记录项的类型
const getHistoryItemType = (item: any) => {
  if (!item) return 'info'
  if (item.new_status_id === 2) return 'warning'  // 暂停
  if (item.new_status_id === 1) return 'success'  // 恢复/进行中
  if (item.new_status_id === 3) return 'danger'   // 终止
  return 'info'
}

// 初始加载
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.demands-page {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .left {
  display: flex;
  align-items: center;
}

.card-header .title {
  font-size: 16px;
  font-weight: bold;
  margin-right: 10px;
}

.card-header .count {
  font-size: 12px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  text-align: right;
}

.history-timeline {
  padding: 20px;
  max-height: 500px;
  overflow-y: auto;
}

.status-change {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.no-history {
  text-align: center;
  color: var(--el-text-color-secondary);
  padding: 40px 0;
}

:deep(.el-timeline-item__content) h4 {
  color: var(--el-text-color-primary);
  margin: 0;
  font-size: 14px;
  line-height: 1.8;
}

:deep(.el-timeline-item__timestamp) {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.mx-2 {
  margin: 0 8px;
}
</style>