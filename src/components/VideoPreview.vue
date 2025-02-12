<template>
  <div class="video-preview">
    <video
      v-if="src"
      :src="getFullUrl(src)"
      controls
      class="preview-video"
    />
    <div v-else class="no-video">
      <el-icon><VideoCamera /></el-icon>
      <span>暂无视频</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { VideoCamera } from '@element-plus/icons-vue'

const props = defineProps<{
  src?: string
}>()

const baseUrl = import.meta.env.VITE_API_URL

const getFullUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${baseUrl}${url}`
}
</script>

<style scoped>
.video-preview {
  width: 100%;
  height: 100%;
  min-height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
}

.preview-video {
  width: 100%;
  height: 100%;
  min-height: 200px;
  object-fit: contain;
}

.no-video {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.no-video .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}
</style> 