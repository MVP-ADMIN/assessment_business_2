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
            :shortcuts="dateShortcuts"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        
        <el-form-item label="需求状态">
          <el-select
            v-model="searchForm.status"
            placeholder="选择状态"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="status in statusOptions"
              :key="status.value"
              :label="status.label"
              :value="status.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="中介状态">
          <el-select
            v-model="searchForm.intermediaryStatus"
            placeholder="选择状态"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="status in intermediaryStatusOptions"
              :key="status.value"
              :label="status.label"
              :value="status.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 搜索和操作栏 -->
    <div class="toolbar">
      <div class="actions">
        <el-button type="primary" @click="$router.push('/demands/create')">
          <el-icon><Plus /></el-icon>新增需求
        </el-button>
        <el-button @click="handleImport">
          <el-icon><Upload /></el-icon>批量导入
        </el-button>
        <el-button @click="handleExport" :loading="exporting">
          <el-icon><Download /></el-icon>导出Excel
        </el-button>
      </div>

      <!-- 添加高级搜索抽屉 -->
      <el-drawer
        v-model="advancedSearchVisible"
        title="高级搜索"
        direction="right"
        size="500px"
      >
        <el-form :model="advancedSearchForm" label-width="100px">
          <el-form-item label="评论数量">
            <el-row :gutter="10">
              <el-col :span="11">
                <el-input-number
                  v-model="advancedSearchForm.minReviews"
                  :min="0"
                  placeholder="最小值"
                />
              </el-col>
              <el-col :span="2" class="text-center">-</el-col>
              <el-col :span="11">
                <el-input-number
                  v-model="advancedSearchForm.maxReviews"
                  :min="0"
                  placeholder="最大值"
                />
              </el-col>
            </el-row>
          </el-form-item>
          
          <el-form-item label="产品价格">
            <el-row :gutter="10">
              <el-col :span="11">
                <el-input-number
                  v-model="advancedSearchForm.minPrice"
                  :min="0"
                  :precision="2"
                  placeholder="最小值"
                />
              </el-col>
              <el-col :span="2" class="text-center">-</el-col>
              <el-col :span="11">
                <el-input-number
                  v-model="advancedSearchForm.maxPrice"
                  :min="0"
                  :precision="2"
                  placeholder="最大值"
                />
              </el-col>
            </el-row>
          </el-form-item>
          
          <el-form-item label="进度">
            <el-select
              v-model="advancedSearchForm.progress"
              placeholder="选择进度"
              clearable
            >
              <el-option label="未开始" value="not_started" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
              <el-option label="已超时" value="overdue" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleAdvancedSearch">
              搜索
            </el-button>
            <el-button @click="resetAdvancedSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </el-drawer>
      
      <!-- 添加数据统计抽屉 -->
      <el-drawer
        v-model="statsVisible"
        title="数据统计"
        direction="right"
        size="800px"
        :destroy-on-close="false"
        @open="handleDrawerOpen"
      >
        <div class="stats-container">
          <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="stats-tabs">
            <el-tab-pane label="状态分布" name="status">
              <div ref="statusChartRef" class="chart-container"></div>
            </el-tab-pane>
            <el-tab-pane label="进度趋势" name="progress">
              <div ref="progressChartRef" class="chart-container"></div>
            </el-tab-pane>
            <el-tab-pane label="评论分析" name="review">
              <div ref="reviewChartRef" class="chart-container"></div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-drawer>
      
      <!-- 添加工具栏按钮 -->
      <div class="toolbar-buttons">
        <el-button @click="advancedSearchVisible = true">
          <el-icon><Search /></el-icon>高级搜索
        </el-button>
        <el-button @click="showStats">
          <el-icon><DataLine /></el-icon>数据统计
        </el-button>
      </div>
    </div>

    <!-- 添加批量操作工具栏 -->
    <div class="batch-toolbar" v-if="selectedRows.length > 0">
      <el-space>
        <span>已选择 {{ selectedRows.length }} 项</span>
        <el-button-group>
          <el-button type="primary" @click="handleBatchStatus">
            批量修改状态
          </el-button>
          <el-button type="danger" @click="handleBatchDelete">
            批量删除
          </el-button>
        </el-button-group>
      </el-space>
    </div>

    <!-- 数据表格 -->
    <el-table
      v-loading="loading"
      :data="demands"
      border
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="marketing_number" label="营销编号" width="180" />
      <el-table-column prop="dingtalk_number" label="钉钉号" width="180" />
      <el-table-column prop="asin" label="ASIN" width="120" />
      <el-table-column prop="assessment_quantity" label="评估数量" width="100" />
      <el-table-column label="评论要求" width="200">
        <template #default="{ row }">
          <div>文字: {{ row.text_review_quantity || 0 }}</div>
          <div>图片: {{ row.image_review_quantity || 0 }}</div>
          <div>视频: {{ row.video_review_quantity || 0 }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="product_price" label="产品价格" width="120">
        <template #default="{ row }">
          ¥{{ row.product_price?.toFixed(2) || '0.00' }}
        </template>
      </el-table-column>
      <el-table-column prop="status_name" label="状态" width="100">
        <template #default="{ row }">
          <el-tag
            :type="getStatusType(row.status_id)"
            effect="light"
            size="small"
            :class="{ 'status-tag': true }"
          >
            {{ row.status_name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="进度" width="200">
        <template #default="{ row }">
          <div>已下单: {{ row.ordered_quantity || 0 }}</div>
          <div>未下单: {{ row.unordered_quantity || 0 }}</div>
          <div>已评价: {{ row.reviewed_quantity || 0 }}</div>
          <div>未评价: {{ row.unreviewed_quantity || 0 }}</div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <el-button-group>
            <el-button
              type="primary"
              link
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              type="primary"
              link
              @click="handleEdit(row)"
              :disabled="row.status_id === 3"
            >
              修改
            </el-button>
            <el-button
              type="warning"
              link
              @click="handlePause(row)"
              :disabled="row.status_id !== 1"
            >
              暂停
            </el-button>
            <el-button
              type="success"
              link
              @click="handleResume(row)"
              :disabled="row.status_id !== 2"
            >
              继续执行
            </el-button>
            <el-button
              type="danger"
              link
              @click="handleStop(row)"
              :disabled="row.status_id === 3 || row.status_id === 4"
            >
              终止
            </el-button>
            <el-button
              type="info"
              link
              @click="handleHistory(row)"
            >
              日志
            </el-button>
          </el-button-group>
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

    <!-- 导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入需求"
      width="500px"
    >
      <el-upload
        class="upload-demo"
        drag
        :action="`${baseUrl}/api/demands/import`"
        :headers="uploadHeaders"
        :on-success="handleImportSuccess"
        :on-error="handleImportError"
        accept=".xlsx"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 xlsx 文件
            <el-button
              type="primary"
              link
              @click.stop="downloadTemplate"
            >
              下载模板
            </el-button>
          </div>
        </template>
      </el-upload>
    </el-dialog>

    <!-- 添加批量修改状态的对话框 -->
    <el-dialog
      v-model="statusDialogVisible"
      title="批量修改状态"
      width="400px"
    >
      <el-form :model="batchForm">
        <el-form-item label="状态">
          <el-select v-model="batchForm.status_id" placeholder="请选择状态">
            <el-option label="进行中" :value="1" />
            <el-option label="已暂停" :value="2" />
            <el-option label="已终止" :value="3" />
            <el-option label="已完成" :value="4" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchStatus" :loading="updating">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加暂停原因对话框 -->
    <el-dialog
      v-model="pauseDialogVisible"
      title="暂停需求"
      width="500px"
    >
      <el-form :model="pauseForm" label-width="80px">
        <el-form-item label="暂停原因" required>
          <el-input
            v-model="pauseForm.reason"
            type="textarea"
            rows="3"
            placeholder="请输入暂停原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pauseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmPause" :loading="pausing">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加继续执行原因对话框 -->
    <el-dialog
      v-model="resumeDialogVisible"
      title="继续执行"
      width="500px"
    >
      <el-form :model="resumeForm" label-width="80px">
        <el-form-item label="执行原因" required>
          <el-input
            v-model="resumeForm.reason"
            type="textarea"
            rows="3"
            placeholder="请输入继续执行的原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resumeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmResume" :loading="resuming">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加终止原因对话框 -->
    <el-dialog
      v-model="stopDialogVisible"
      title="终止需求"
      width="500px"
    >
      <el-form :model="stopForm" label-width="80px">
        <el-form-item label="终止原因" required>
          <el-input
            v-model="stopForm.reason"
            type="textarea"
            rows="3"
            placeholder="请输入终止原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stopDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmStop" :loading="stopping">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 修改历史记录对话框为日志表格 -->
    <el-drawer
      v-model="historyDialogVisible"
      title="状态变更日志"
      direction="right"
      size="800px"
    >
      <div class="history-container">
        <el-table
          :data="historyList"
          border
          style="width: 100%"
          max-height="calc(100vh - 200px)"
        >
          <el-table-column
            prop="change_time"
            label="变更时间"
            width="180"
            sortable
          >
            <template #default="{ row }">
              {{ formatDateTime(row.change_time) }}
            </template>
          </el-table-column>
          <el-table-column
            label="状态变更"
            width="200"
            align="center"
            :filters="statusFilters"
            :filter-method="filterStatus"
          >
            <template #default="{ row }">
              <div class="status-change">
                <el-tag size="small" :type="getStatusType(row.old_status_id)">
                  {{ row.old_status_name }}
                </el-tag>
                <el-icon class="mx-2"><ArrowRight /></el-icon>
                <el-tag size="small" :type="getStatusType(row.new_status_id)">
                  {{ row.new_status_name }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column
            prop="change_description"
            label="变更原因"
            show-overflow-tooltip
          />
        </el-table>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import type { Demand } from '../../types/demand'
import * as echarts from 'echarts'
import type { StatusChartData, ProgressChartData, ReviewChartData } from '@/types/chart'
import { reactive, ref, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Search, Plus, Upload, Download, Refresh } from '@element-plus/icons-vue'

const baseUrl = import.meta.env.VITE_API_URL

// 搜索表单
const searchForm = reactive({
  keyword: '',
  dateRange: null,
  status: null,
  intermediaryStatus: null
})

// 表格数据
const demands = ref<Demand[]>([])
const loading = ref(false)
const exporting = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 导入对话框
const importDialogVisible = ref(false)
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

// 批量操作相关
const selectedRows = ref<Demand[]>([])
const statusDialogVisible = ref(false)
const updating = ref(false)
const batchForm = reactive({
  status_id: null as number | null
})

// 高级搜索相关
const advancedSearchVisible = ref(false)
const advancedSearchForm = reactive({
  minReviews: null as number | null,
  maxReviews: null as number | null,
  minPrice: null as number | null,
  maxPrice: null as number | null,
  progress: null as string | null
})

// 数据统计相关
const statsVisible = ref(false)
const statusChartRef = ref<HTMLElement>()
const progressChartRef = ref<HTMLElement>()
const reviewChartRef = ref<HTMLElement>()

let statusChart: echarts.ECharts | null = null
let progressChart: echarts.ECharts | null = null
let reviewChart: echarts.ECharts | null = null

// 添加 tab 相关的状态
const activeTab = ref('status')
let statsData = ref(null)

// 暂停相关
const pauseDialogVisible = ref(false)
const pausing = ref(false)
const pauseForm = reactive({
  reason: '',
  demandId: null as number | null
})

// 继续执行相关
const resumeDialogVisible = ref(false)
const resuming = ref(false)
const resumeForm = reactive({
  reason: '',
  demandId: null as number | null
})

// 终止相关
const stopDialogVisible = ref(false)
const stopping = ref(false)
const stopForm = reactive({
  reason: '',
  demandId: null as number | null
})

// 历史记录相关
const historyDialogVisible = ref(false)
const historyList = ref([])

const router = useRouter()

// 需求状态选项
const statusOptions = [
  { value: 1, label: '进行中' },
  { value: 2, label: '已暂停' },
  { value: 3, label: '已完成' },
  { value: 4, label: '已取消' }
]

// 中介状态选项
const intermediaryStatusOptions = [
  { value: 1, label: '未开始' },
  { value: 2, label: '进行中' },
  { value: 3, label: '已取消' },
  { value: 4, label: '已完成' }
]

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    }
  }
]

// 状态类型映射
const STATUS_MAP = {
  1: { type: 'success', name: '进行中' },
  2: { type: 'warning', name: '已暂停' },
  3: { type: 'danger', name: '已终止' },
  4: { type: 'info', name: '已完成' }
} as const

// 获取状态类型
const getStatusType = (statusId: number) => {
  return STATUS_MAP[statusId as keyof typeof STATUS_MAP]?.type || ''
}

// 获取状态名称
const getStatusName = (statusId: number) => {
  return STATUS_MAP[statusId as keyof typeof STATUS_MAP]?.name || '未知'
}

// 检查操作权限
const canPause = (row: Demand) => row.status_id === 1
const canResume = (row: Demand) => row.status_id === 2
const canStop = (row: Demand) => ![3, 4].includes(row.status_id)
const canEdit = (row: Demand) => row.status_id !== 3

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      keyword: searchForm.keyword,
      status: searchForm.status,
      intermediaryStatus: searchForm.intermediaryStatus,
      start_date: searchForm.dateRange?.[0]?.toISOString().split('T')[0],
      end_date: searchForm.dateRange?.[1]?.toISOString().split('T')[0]
    }
    
    const { data: response } = await axios.get('/api/demands', { params })
    console.log('Response:', response) // 添加日志
    if (response.code === 0 && response.data) {
      demands.value = response.data.items || []
      total.value = response.data.total || 0
    } else {
      demands.value = []
      total.value = 0
      ElMessage.error(response.message || '加载数据失败')
    }
  } catch (error) {
    console.error('Failed to load demands:', error)
    demands.value = []
    total.value = 0
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
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.dateRange = null
  searchForm.status = null
  searchForm.intermediaryStatus = null
  currentPage.value = 1
  loadData()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadData()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadData()
}

// 导入处理
const handleImport = () => {
  importDialogVisible.value = true
}

const handleImportSuccess = (response: any) => {
  if (response.code === 0) {
    ElMessage.success('导入成功')
    importDialogVisible.value = false
    loadData()
  } else {
    ElMessage.error(response.message || '导入失败')
  }
}

const handleImportError = () => {
  ElMessage.error('导入失败')
}

// 导出处理
const handleExport = async () => {
  try {
    exporting.value = true
    const params = {
      keyword: searchForm.keyword,
      status: searchForm.status,
      intermediaryStatus: searchForm.intermediaryStatus,
      start_date: searchForm.dateRange?.[0]?.toISOString().split('T')[0],
      end_date: searchForm.dateRange?.[1]?.toISOString().split('T')[0]
    }
    
    const { data } = await axios.get('/api/demands/export', {
      params,
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `需求列表_${new Date().toISOString().split('T')[0]}.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Failed to export demands:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 删除处理
const handleDelete = (row: Demand) => {
  ElMessageBox.confirm(
    '确定要删除该需求吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.delete(`/api/demands/${row.demand_id}`)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('Failed to delete demand:', error)
      ElMessage.error('删除失败')
    }
  })
}

// 选择变化处理
const handleSelectionChange = (rows: Demand[]) => {
  selectedRows.value = rows
}

// 批量修改状态
const handleBatchStatus = () => {
  statusDialogVisible.value = true
}

const confirmBatchStatus = async () => {
  if (!batchForm.status_id) {
    ElMessage.warning('请选择状态')
    return
  }

  try {
    updating.value = true
    const demandIds = selectedRows.value.map(row => row.demand_id)
    await axios.put('/api/demands/batch/status', {
      demand_ids: demandIds,
      status_id: batchForm.status_id
    })
    
    ElMessage.success('修改成功')
    statusDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('Failed to update status:', error)
    ElMessage.error('修改失败')
  } finally {
    updating.value = false
  }
}

// 批量删除
const handleBatchDelete = () => {
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedRows.value.length} 条需求吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const demandIds = selectedRows.value.map(row => row.demand_id)
      await axios.delete('/api/demands/batch', {
        data: { demand_ids: demandIds }
      })
      
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('Failed to delete demands:', error)
      ElMessage.error('删除失败')
    }
  })
}

// 高级搜索处理
const handleAdvancedSearch = () => {
  currentPage.value = 1
  loadData()
  advancedSearchVisible.value = false
}

const resetAdvancedSearch = () => {
  advancedSearchForm.minReviews = null
  advancedSearchForm.maxReviews = null
  advancedSearchForm.minPrice = null
  advancedSearchForm.maxPrice = null
  advancedSearchForm.progress = null
}

// 数据统计处理
const showStats = async () => {
  statsVisible.value = true
  try {
    const { data: response } = await axios.get('/api/demands/stats')
    console.log('Stats response:', response) // 添加日志
    if (response.code === 0 && response.data) {
      // 确保图表容器已经渲染
      await nextTick()
      initStatusChart(response.data.status)
      initProgressChart(response.data.progress)
      initReviewChart(response.data.reviews)
    } else {
      ElMessage.error(response.message || '加载统计数据失败')
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
    ElMessage.error('加载统计数据失败')
    statsVisible.value = false
  }
}

// 初始化状态图表
const initStatusChart = (data: StatusChartData[]) => {
  if (!statusChartRef.value) return
  try {
    statusChart = echarts.init(statusChartRef.value)
    statusChart.setOption({
      title: { 
        text: '需求状态分布',
        left: 'center'
      },
      tooltip: { 
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: { 
        orient: 'horizontal',
        bottom: 'bottom'
      },
      series: [{
        name: '状态分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        data
      }]
    })
  } catch (error) {
    console.error('Failed to init status chart:', error)
  }
}

// 初始化进度趋势图表
const initProgressChart = (data: ProgressChartData[]) => {
  if (!progressChartRef.value) return
  try {
    const dates = data.map(item => item.date).reverse()
    const totals = data.map(item => item.total).reverse()
    const completed = data.map(item => item.completed).reverse()

    progressChart = echarts.init(progressChartRef.value)
    progressChart.setOption({
      title: { 
        text: '进度趋势',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
      },
      legend: {
        data: ['总数', '已完成'],
        bottom: 'bottom'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '60px',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: dates,
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '总数',
          type: 'line',
          smooth: true,
          data: totals,
          itemStyle: {
            color: '#409EFF'
          }
        },
        {
          name: '已完成',
          type: 'line',
          smooth: true,
          data: completed,
          itemStyle: {
            color: '#67C23A'
          }
        }
      ]
    })
  } catch (error) {
    console.error('Failed to init progress chart:', error)
  }
}

// 初始化评论类型图表
const initReviewChart = (data: ReviewChartData[]) => {
  if (!reviewChartRef.value) return
  try {
    const chartData = data.map(item => ({
      name: item.type === 'text' ? '文字评论' :
            item.type === 'image' ? '图片评论' : '视频评论',
      value: item.count
    }))

    reviewChart = echarts.init(reviewChartRef.value)
    reviewChart.setOption({
      title: { 
        text: '评论类型分布',
        left: 'center'
      },
      tooltip: { 
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'horizontal',
        bottom: 'bottom'
      },
      series: [{
        name: '评论类型',
        type: 'pie',
        radius: '50%',
        data: chartData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        }
      }]
    })
  } catch (error) {
    console.error('Failed to init review chart:', error)
  }
}

// 监听窗口大小变化，重绘图表
const handleResize = () => {
  statusChart?.resize()
  progressChart?.resize()
  reviewChart?.resize()
}

window.addEventListener('resize', handleResize)

// 组件卸载时清理
onMounted(() => {
  loadData() // 改为加载列表数据
})

onUnmounted(() => {
  statusChart?.dispose()
  progressChart?.dispose()
  reviewChart?.dispose()
  window.removeEventListener('resize', handleResize)
})

// 处理抽屉打开事件
const handleDrawerOpen = async () => {
  await loadStatsData()
}

// 处理标签页切换
const handleTabClick = () => {
  if (!statsData.value) return
  
  nextTick(() => {
    switch (activeTab.value) {
      case 'status':
        initStatusChart(statsData.value.status)
        break
      case 'progress':
        initProgressChart(statsData.value.progress)
        break
      case 'review':
        initReviewChart(statsData.value.reviews)
        break
    }
  })
}

// 加载统计数据
const loadStatsData = async () => {
  try {
    const { data: response } = await axios.get('/api/demands/stats')
    console.log('Stats response:', response)
    if (response.code === 0 && response.data) {
      statsData.value = response.data
      await nextTick()
      handleTabClick() // 初始化当前标签页的图表
    } else {
      ElMessage.error(response.message || '加载统计数据失败')
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
    ElMessage.error('加载统计数据失败')
  }
}

// 查看功能
const handleView = (row: Demand) => {
  router.push({
    name: 'DemandDetail',
    params: { id: String(row.demand_id) }
  })
}

// 修改功能
const handleEdit = (row: Demand) => {
  router.push({
    name: 'EditDemand',
    params: { id: String(row.demand_id) }
  })
}

// 暂停功能
const handlePause = async (row: Demand) => {
  try {
    await ElMessageBox.confirm(
      '确定要暂停该需求吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    pauseForm.demandId = row.demand_id
    pauseForm.reason = ''
    pauseDialogVisible.value = true
  } catch {
    // 用户取消操作
  }
}

const confirmPause = async () => {
  if (!pauseForm.reason.trim()) {
    ElMessage.warning('请输入暂停原因')
    return
  }

  try {
    pausing.value = true
    const { data: response } = await axios.post(`/api/demands/${pauseForm.demandId}/pause`, {
      reason: pauseForm.reason
    })
    
    if (response.code === 0) {
      ElMessage.success('已暂停')
      pauseDialogVisible.value = false
      await loadData() // 重新加载数据
    } else {
      ElMessage.error(response.message || '暂停失败')
    }
  } catch (error) {
    console.error('Failed to pause demand:', error)
    ElMessage.error('暂停失败')
  } finally {
    pausing.value = false
  }
}

// 继续执行功能
const handleResume = async (row: Demand) => {
  try {
    await ElMessageBox.confirm(
      '确定要继续执行该需求吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    resumeForm.demandId = row.demand_id
    resumeForm.reason = ''
    resumeDialogVisible.value = true
  } catch {
    // 用户取消操作
  }
}

const confirmResume = async () => {
  if (!resumeForm.reason.trim()) {
    ElMessage.warning('请输入继续执行的原因')
    return
  }

  try {
    resuming.value = true
    const { data: response } = await axios.post(`/api/demands/${resumeForm.demandId}/resume`, {
      reason: resumeForm.reason
    })
    
    if (response.code === 0) {
      ElMessage.success('已继续执行')
      resumeDialogVisible.value = false
      await loadData()
    } else {
      ElMessage.error(response.message || '操作失败')
    }
  } catch (error) {
    console.error('Failed to resume demand:', error)
    ElMessage.error('操作失败')
  } finally {
    resuming.value = false
  }
}

// 终止功能
const handleStop = async (row: Demand) => {
  try {
    await ElMessageBox.confirm(
      '确定要终止该需求吗？终止后不可恢复',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    stopForm.demandId = row.demand_id
    stopForm.reason = ''
    stopDialogVisible.value = true
  } catch {
    // 用户取消操作
  }
}

const confirmStop = async () => {
  if (!stopForm.reason.trim()) {
    ElMessage.warning('请输入终止原因')
    return
  }

  try {
    stopping.value = true
    const { data: response } = await axios.post(`/api/demands/${stopForm.demandId}/stop`, {
      reason: stopForm.reason
    })
    
    if (response.code === 0) {
      ElMessage.success('已终止')
      stopDialogVisible.value = false
      await loadData()
    } else {
      ElMessage.error(response.message || '终止失败')
    }
  } catch (error) {
    console.error('Failed to stop demand:', error)
    ElMessage.error('终止失败')
  } finally {
    stopping.value = false
  }
}

// 查看历史记录
const handleHistory = async (row: Demand) => {
  try {
    const { data: response } = await axios.get(`/api/demands/${row.demand_id}/history`)
    if (response.code === 0) {
      historyList.value = response.data
      historyDialogVisible.value = true
    } else {
      ElMessage.error(response.message || '获取历史记录失败')
    }
  } catch (error) {
    console.error('Failed to get history:', error)
    ElMessage.error('获取历史记录失败')
  }
}

// 格式化日期时间
const formatDateTime = (datetime: string) => {
  return new Date(datetime).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 状态过滤选项
const statusFilters = [
  { text: '进行中', value: 1 },
  { text: '已暂停', value: 2 },
  { text: '已终止', value: 3 },
  { text: '已完成', value: 4 }
]

// 状态过滤方法
const filterStatus = (value: number, row: any) => {
  return row.new_status_id === value
}

// 下载模板
const downloadTemplate = async () => {
  try {
    const response = await axios.get('/api/demands/template', {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '需求导入模板.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to download template:', error)
    ElMessage.error('下载模板失败')
  }
}
</script>

<style scoped>
.demands-page {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.el-upload__tip {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-demo {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.el-upload__text {
  margin: 8px 0;
  color: var(--el-text-color-regular);
}

.el-upload__text em {
  color: var(--el-color-primary);
  font-style: normal;
}

.batch-toolbar {
  background-color: #f5f7fa;
  padding: 8px 16px;
  margin-bottom: 16px;
  border-radius: 4px;
}

.toolbar-buttons {
  display: flex;
  gap: 8px;
}

.text-center {
  text-align: center;
  line-height: 32px;
}

.text-gray {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.status-change {
  display: flex;
  align-items: center;
  justify-content: center;
}

.mx-2 {
  margin: 0 8px;
}

/* 添加禁用状态的样式 */
.el-button.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 添加状态标签的样式 */
.el-tag {
  min-width: 60px;
  text-align: center;
}

.status-tag {
  min-width: 70px;
  text-align: center;
  padding: 0 10px;
  border-radius: 12px;
}

/* 添加状态标签的悬停效果 */
.status-tag:hover {
  opacity: 0.8;
  transform: scale(1.05);
  transition: all 0.2s ease;
}

/* 数据统计样式 */
.stats-container {
  height: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.stats-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.stats-tabs :deep(.el-tabs__content) {
  flex: 1;
  padding: 20px 0;
}

.chart-container {
  width: 100%;
  height: calc(100vh - 300px);
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 日志样式 */
.history-container {
  height: 100%;
  padding: 20px;
}

.history-container :deep(.el-table) {
  --el-table-border-color: var(--el-border-color-lighter);
  --el-table-header-bg-color: var(--el-fill-color-light);
}

.history-container :deep(.el-table__header) {
  position: sticky;
  top: 0;
  z-index: 1;
}

.status-change {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.status-change .el-tag {
  min-width: 60px;
}

.mx-2 {
  color: var(--el-text-color-secondary);
}

/* 抽屉样式优化 */
:deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 16px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

:deep(.el-drawer__body) {
  padding: 0;
  overflow: hidden;
}

:deep(.el-tabs__nav-wrap) {
  padding: 0 20px;
}

:deep(.el-tabs__content) {
  overflow: auto;
}

/* 图表容器动画 */
.chart-container {
  transition: all 0.3s ease;
}

.chart-container:hover {
  transform: scale(1.01);
}

/* 表格行悬停效果 */
.history-container :deep(.el-table__row:hover) {
  background-color: var(--el-fill-color-lighter) !important;
}

/* 状态标签动画 */
.status-change .el-tag {
  transition: all 0.3s ease;
}

.status-change .el-tag:hover {
  transform: scale(1.05);
}
</style>