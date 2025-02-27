<template>
  <div class="upload-image">
    <el-upload
      v-if="!readonly"
      class="image-uploader"
      :action="`${baseUrl}/api/upload/image`"
      :headers="headers"
      name="file"
      :show-file-list="true"
      :before-upload="beforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      :multiple="multiple"
      :limit="limit"
      list-type="picture"
      accept="image/*"
    >
      <div class="upload-content">
        <el-icon class="upload-icon"><Plus /></el-icon>
        <div class="upload-text">点击上传</div>
      </div>
    </el-upload>
    
    <!-- 只读模式下的预览 -->
    <div v-else class="preview-list">
      <template v-if="multiple && Array.isArray(modelValue)">
        <el-image
          v-for="(url, index) in modelValue"
          :key="index"
          :src="getImageUrl(url)"
          :preview-src-list="modelValue.map(getImageUrl)"
          fit="cover"
          class="preview-image"
        />
      </template>
      <el-image
        v-else-if="modelValue"
        :src="getImageUrl(modelValue as string)"
        fit="cover"
        class="preview-image"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Upload, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { UploadProps } from 'element-plus'

const props = withDefaults(defineProps<{
  modelValue?: string | string[]
  readonly?: boolean
  multiple?: boolean
  limit?: number
}>(), {
  readonly: false,
  multiple: false,
  limit: 1
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | string[]): void
  (e: 'success', url: string): void
  (e: 'error', error: any): void
}>()

const baseUrl = import.meta.env.VITE_API_URL || 'http://192.168.1.20:5000'
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
    if (props.multiple) {
      const currentValue = Array.isArray(props.modelValue) ? props.modelValue : []
      emit('update:modelValue', [...currentValue, url])
    } else {
      emit('update:modelValue', url)
    }
    emit('success', url)
    ElMessage.success('上传成功')
  } else {
    handleError(response)
  }
}

const handleError: UploadProps['onError'] = (error) => {
  console.error('Upload failed:', error)
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
  width: 100%;
}

.image-uploader {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration);
}

.image-uploader:hover {
  border-color: var(--el-color-primary);
}

.upload-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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

.preview-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.preview-image {
  width: 100px;
  height: 100px;
  border-radius: 4px;
  object-fit: cover;
}

:deep(.el-upload-list) {
  margin-top: 10px;
}

:deep(.el-upload-list__item) {
  transition: all 0.3s;
}

:deep(.el-upload-list__item:hover) {
  transform: translateY(-2px);
}
</style> 