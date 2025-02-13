<template>
  <div class="image-upload">
    <el-upload
      v-if="!readonly"
      v-model:file-list="fileList"
      class="upload-demo"
      :action="`${baseUrl}/api/upload/image`"
      :headers="headers"
      :before-upload="handleBeforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-remove="handleRemove"
      :limit="limit"
      :multiple="multiple"
      list-type="picture"
      name="file"
    >
      <template #trigger>
        <el-button type="primary">选择图片</el-button>
      </template>
      <template #tip>
        <div class="el-upload__tip">
          只能上传 jpg/png 文件，且不超过 5MB
        </div>
      </template>
    </el-upload>
    
    <!-- 只读模式下的预览 -->
    <div v-else class="preview-list">
      <template v-if="multiple">
        <el-image
          v-for="(url, index) in modelValue"
          :key="index"
          :src="getImageUrl(url)"
          :preview-src-list="Array.isArray(modelValue) ? modelValue.map(getImageUrl) : []"
          fit="cover"
          class="preview-image"
        />
      </template>
      <el-image
        v-else
        :src="getImageUrl(modelValue as string)"
        fit="cover"
        class="preview-image"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadProps, UploadUserFile } from 'element-plus'

const props = defineProps<{
  modelValue?: string | string[]
  readonly?: boolean
  multiple?: boolean
  limit?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | string[]]
  'success': [url: string]
  'error': [error: any]
}>()

const baseUrl = import.meta.env.VITE_API_URL || ''
const headers = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

const fileList = ref<UploadUserFile[]>([])

const handleBeforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

const handleSuccess: UploadProps['onSuccess'] = (response) => {
  if (response.code === 0) {
    const url = response.data.url
    if (props.multiple) {
      const newValue = Array.isArray(props.modelValue) ? [...props.modelValue, url] : [url]
      emit('update:modelValue', newValue)
    } else {
      emit('update:modelValue', url)
    }
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

const handleRemove: UploadProps['onRemove'] = (file) => {
  if (props.multiple && Array.isArray(props.modelValue)) {
    const index = fileList.value.indexOf(file)
    const newValue = [...props.modelValue]
    newValue.splice(index, 1)
    emit('update:modelValue', newValue)
  } else {
    emit('update:modelValue', '')
  }
}

const getImageUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return `${baseUrl}${url}`
}
</script>

<style scoped>
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