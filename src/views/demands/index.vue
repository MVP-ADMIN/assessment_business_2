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
        <el-table-column label="操作" width="260" fixed="right">
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
              v-if="row.status_id === DemandStatus.PROCESSING"
              link
              type="warning"
              @click="handlePause(row.demand_id)"
            >
              暂停
            </el-button>
            <el-button
              v-if="row.status_id === DemandStatus.PAUSED"
              link
              type="success"
              @click="handleResume(row.demand_id)"
            >
              恢复
            </el-button>
            <el-button 
              link 
              type="danger" 
              @click="handleDelete(row.demand_id)"
            >
              删除
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
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
  { value: DemandStatus.PENDING, label: '待处理' },
  { value: DemandStatus.PROCESSING, label: '进行中' },
  { value: DemandStatus.PAUSED, label: '已暂停' },
  { value: DemandStatus.COMPLETED, label: '已完成' },
  { value: DemandStatus.CANCELLED, label: '已取消' }
]

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
const handlePause = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要暂停这条需求吗？', '提示', {
      type: 'warning'
    })
    await demandApi.pause(id)
    ElMessage.success('已暂停')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to pause demand:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 恢复需求
const handleResume = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要恢复这条需求吗？', '提示', {
      type: 'warning'
    })
    await demandApi.resume(id)
    ElMessage.success('已恢复')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to resume demand:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 获取状态类型
const getStatusType = (statusId: number) => {
  const types: Record<number, '' | 'success' | 'warning' | 'danger'> = {
    [DemandStatus.PENDING]: '',           // 待处理
    [DemandStatus.PROCESSING]: 'warning', // 进行中
    [DemandStatus.PAUSED]: 'info',        // 已暂停
    [DemandStatus.COMPLETED]: 'success',  // 已完成
    [DemandStatus.CANCELLED]: 'danger'    // 已取消
  }
  return types[statusId] || ''
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
</style>