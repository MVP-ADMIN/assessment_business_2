<template>
  <div class="image-preview">
    <el-image
      v-if="src"
      :src="getFullUrl(src)"
      :preview-src-list="[getFullUrl(src)]"
      fit="cover"
      class="preview-image"
    >
      <template #placeholder>
        <div class="image-placeholder">
          <el-icon><Picture /></el-icon>
          <span>加载中...</span>
        </div>
      </template>
      <template #error>
        <div class="image-error">
          <el-icon><Picture /></el-icon>
          <span>加载失败</span>
        </div>
      </template>
    </el-image>
    <div v-else class="no-image">
      <el-icon><Picture /></el-icon>
      <span>暂无图片</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Picture } from '@element-plus/icons-vue'

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
.image-preview {
  width: 100%;
  height: 100%;
  min-height: 120px;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  min-height: 120px;
}

.image-placeholder,
.image-error,
.no-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  min-height: 120px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  background-color: var(--el-fill-color-light);
}

.image-placeholder .el-icon,
.image-error .el-icon,
.no-image .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

:deep(.el-image) {
  width: 100%;
  height: 100%;
}

:deep(.el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style> 