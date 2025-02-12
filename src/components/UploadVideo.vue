<template>
  <div class="upload-video">
    <el-upload
      class="video-uploader"
      :action="`${baseUrl}/api/upload/video`"
      :headers="headers"
      name="file"
      :show-file-list="false"
      :before-upload="beforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      accept="video/*"
    >
      <video
        v-if="modelValue"
        :src="getVideoUrl(modelValue)"
        class="preview-video"
        controls
      />
      <el-icon v-else class="upload-icon"><Plus /></el-icon>
    </el-upload>
    
    <div v-if="modelValue" class="actions">
      <el-button type="danger" link @click="handleRemove">
        删除
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const baseUrl = import.meta.env.VITE_API_URL

const headers = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

const getVideoUrl = (url: string) => {
  if (url.startsWith('http')) return url
  return baseUrl + url
}

const beforeUpload = (file: File) => {
  const isVideo = file.type.startsWith('video/')
  const isLt100M = file.size / 1024 / 1024 < 100

  if (!isVideo) {
    ElMessage.error('只能上传视频文件!')
    return false
  }
  if (!isLt100M) {
    ElMessage.error('视频大小不能超过 100MB!')
    return false
  }
  return true
}

const handleSuccess = (response: any) => {
  if (response.code === 0) {
    emit('update:modelValue', response.data.url)
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

const handleError = () => {
  ElMessage.error('上传失败')
}

const handleRemove = () => {
  emit('update:modelValue', '')
}
</script>

<style scoped>
.upload-video {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.video-uploader {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration);
}

.video-uploader:hover {
  border-color: var(--el-color-primary);
}

.preview-video {
  width: 100%;
  max-width: 360px;
  max-height: 200px;
  object-fit: contain;
}

.upload-icon {
  font-size: 28px;
  color: #8c939d;
  width: 360px;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.actions {
  display: flex;
  justify-content: center;
}
</style> 