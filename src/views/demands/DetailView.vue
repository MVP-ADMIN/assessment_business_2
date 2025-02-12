<template>
  <div class="detail-view">
    <div class="header">
      <h2>测评明细详情</h2>
      <el-button @click="router.back()">返回</el-button>
    </div>

    <el-descriptions v-if="detail" :column="3" border>
      <el-descriptions-item label="订单号" :span="1">
        {{ detail.order_number }}
      </el-descriptions-item>
      <el-descriptions-item label="订单金额" :span="1">
        ¥{{ detail.order_amount }}
      </el-descriptions-item>
      <el-descriptions-item label="状态" :span="1">
        <detail-status-tag :status="detail.status" />
      </el-descriptions-item>
      
      <el-descriptions-item label="下单时间" :span="1">
        {{ formatDateTime(detail.order_time) }}
      </el-descriptions-item>
      <el-descriptions-item label="评论时间" :span="1">
        {{ formatDateTime(detail.review_time) }}
      </el-descriptions-item>
      <el-descriptions-item label="备注" :span="1">
        {{ detail.remark }}
      </el-descriptions-item>
    </el-descriptions>

    <el-card v-if="detail" class="content-card">
      <template #header>
        <div class="card-header">
          <span>评论内容</span>
        </div>
      </template>
      <div class="review-content">{{ detail.review_content }}</div>
    </el-card>

    <el-row :gutter="20" class="preview-row">
      <el-col :span="8">
        <el-card>
          <template #header>评论图片</template>
          <image-preview :src="detail?.review_images?.[0]" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>评论视频</template>
          <video-preview :src="detail?.review_video" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>支付截图</template>
          <image-preview :src="detail?.payment_screenshot" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="preview-row">
      <el-col :span="12">
        <el-card>
          <template #header>订单截图</template>
          <image-preview :src="detail?.order_screenshot" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>评论截图</template>
          <image-preview :src="detail?.review_screenshot" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import DetailStatusTag from '@/components/DetailStatusTag.vue'
import ImagePreview from '@/components/ImagePreview.vue'
import VideoPreview from '@/components/VideoPreview.vue'
import type { DemandDetail } from '@/types/detail'

const router = useRouter()
const route = useRoute()
const detail = ref<DemandDetail | null>(null)

const formatDateTime = (date: string | null) => {
  if (!date) return ''
  return new Date(date).toLocaleString()
}

const loadDetail = async () => {
  try {
    const { data: response } = await axios.get(`/api/demand-details/${route.params.detailId}`)
    if (response.code === 0) {
      detail.value = response.data
    } else {
      ElMessage.error(response.message || '加载失败')
    }
  } catch (error) {
    console.error('Failed to load detail:', error)
    ElMessage.error('加载失败')
  }
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.detail-view {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-card {
  margin: 20px 0;
}

.review-content {
  white-space: pre-wrap;
  min-height: 60px;
}

.preview-row {
  margin-top: 20px;
}

:deep(.el-card__header) {
  padding: 12px 20px;
  font-weight: 500;
}
</style> 