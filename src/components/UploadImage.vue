<template>
  <div class="upload-image">
    <el-upload
      class="image-uploader"
      :action="`${baseUrl}/api/upload/image`"
      :headers="headers"
      name="file"
      :show-file-list="false"
      :before-upload="beforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      accept="image/*"
    >
      <div class="upload-content">
        <img v-if="modelValue" :src="getImageUrl(modelValue)" class="preview-image" />
        <div v-else class="upload-placeholder">
          <el-icon class="upload-icon"><Plus /></el-icon>
          <div class="upload-text">点击上传</div>
        </div>
      </div>
    </el-upload>
  </div>
</template>

<script setup lang="ts">
import { Upload, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { UploadProps } from 'element-plus'

const props = withDefaults(defineProps<{
  buttonText?: string
  limit?: number
  multiple?: boolean
  listType?: 'text' | 'picture' | 'picture-card'
  showFileList?: boolean
  modelValue?: string
}>(), {
  buttonText: '上传图片',
  limit: 1,
  multiple: false,
  listType: 'text',
  showFileList: true,
  modelValue: ''
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'success', url: string): void
  (e: 'error', error: any): void
}>()

const baseUrl = import.meta.env.VITE_API_URL
const headers = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

const handleSuccess: UploadProps['onSuccess'] = (response) => {
  if (response.code === 0) {
    const url = response.data.url
    emit('update:modelValue', url)
    emit('success', url)
    ElMessage.success('上传成功')
  } else {
    emit('error', response.message)
    ElMessage.error(response.message || '上传失败')
  }
}

const handleError: UploadProps['onError'] = (error) => {
  emit('error', error)
  ElMessage.error('上传失败')
}

const getImageUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${baseUrl}${url}`
}
</script>

<style scoped>
.upload-image {
  width: 178px;
  height: 178px;
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration);
}

.upload-image:hover {
  border-color: var(--el-color-primary);
}

.upload-content {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.upload-icon {
  font-size: 28px;
  color: #8c939d;
}

.upload-text {
  color: #8c939d;
  font-size: 12px;
  margin-top: 8px;
}

:deep(.el-upload) {
  width: 100%;
  height: 100%;
}
</style> 