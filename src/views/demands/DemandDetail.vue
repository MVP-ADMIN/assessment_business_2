<template>
  <div class="demand-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <h2>需求详情</h2>
          <div class="actions">
            <el-button 
              type="primary" 
              @click="$router.push(`/demands/${id}/edit`)"
            >
              编辑
            </el-button>
            <el-button @click="$router.push('/demands')">
              返回
            </el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="3" border>
        <el-descriptions-item label="营销编号">
          {{ demand?.marketing_number }}
        </el-descriptions-item>
        <el-descriptions-item label="钉钉号">
          {{ demand?.dingtalk_number }}
        </el-descriptions-item>
        <el-descriptions-item label="ASIN">
          {{ demand?.asin }}
        </el-descriptions-item>
        
        <el-descriptions-item label="评估数量">
          {{ demand?.assessment_quantity }}
        </el-descriptions-item>
        <el-descriptions-item label="文字评论数">
          {{ demand?.text_review_quantity }}
        </el-descriptions-item>
        <el-descriptions-item label="图片评论数">
          {{ demand?.image_review_quantity }}
        </el-descriptions-item>
        
        <el-descriptions-item label="视频评论数">
          {{ demand?.video_review_quantity }}
        </el-descriptions-item>
        <el-descriptions-item label="产品价格">
          {{ demand?.product_price }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(demand?.status_id)">
            {{ demand?.status_name }}
          </el-tag>
        </el-descriptions-item>
        
        <el-descriptions-item label="搜索关键词" :span="3">
          {{ demand?.search_keyword }}
        </el-descriptions-item>
        
        <el-descriptions-item label="链接" :span="3">
          <el-link type="primary" :href="demand?.hyperlink" target="_blank">
            {{ demand?.hyperlink }}
          </el-link>
        </el-descriptions-item>
        
        <el-descriptions-item label="备注" :span="3">
          {{ demand?.other_notes }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 测评明细列表 -->
      <div class="details-section">
        <div class="section-header">
          <h3>测评明细</h3>
          <el-button 
            type="primary"
            @click="$router.push(`/demands/${id}/details/create`)"
          >
            新增明细
          </el-button>
        </div>

        <el-table :data="details" border>
          <el-table-column prop="order_number" label="订单号" />
          <el-table-column prop="order_amount" label="订单金额" />
          <el-table-column prop="order_time" label="下单时间" />
          <el-table-column prop="review_time" label="评论时间" />
          <el-table-column label="状态">
            <template #default="{ row }">
              <detail-status-tag :status="row.status" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button 
                link 
                type="primary" 
                @click="$router.push(`/demands/${id}/details/${row.detail_id}`)"
              >
                查看
              </el-button>
              <el-button 
                link 
                type="primary" 
                @click="$router.push(`/demands/${id}/details/${row.detail_id}/edit`)"
              >
                编辑
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <el-card class="content-card">
      <template #header>
        <div class="card-header">
          <span>评论内容</span>
        </div>
      </template>
      <div class="review-content">{{ detail?.review_content }}</div>
    </el-card>

    <el-row :gutter="20" class="preview-row">
      <el-col :span="8">
        <el-card>
          <template #header>评论图片</template>
          <UploadImage 
            :modelValue="detail?.review_images"
            readonly
            multiple
          />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>评论视频</template>
          <UploadVideo 
            :modelValue="detail?.review_video"
            readonly
          />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>支付截图</template>
          <UploadImage 
            :modelValue="detail?.payment_screenshot"
            readonly
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { demandApi } from '@/api/demand'
import DetailStatusTag from '@/components/DetailStatusTag.vue'
import { DemandStatus } from '@/types/demand'
import UploadImage from '@/components/UploadImage.vue'
import UploadVideo from '@/components/UploadVideo.vue'

const route = useRoute()
const id = route.params.id as string
const loading = ref(false)
const demand = ref<any>(null)
const details = ref([])
const detail = ref<any>(null)

const loadData = async () => {
  try {
    loading.value = true
    const data = await demandApi.detail(Number(id))
    demand.value = data
    // 加载测评明细
    const detailsData = await demandApi.getDetails(Number(id))
    details.value = detailsData
    detail.value = detailsData[0]
  } catch (error) {
    console.error('Failed to load demand:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

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

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.demand-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.details-section {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
}

.content-card {
  margin-top: 20px;
}

.review-content {
  padding: 20px;
}

.preview-row {
  margin-top: 20px;
}
</style> 