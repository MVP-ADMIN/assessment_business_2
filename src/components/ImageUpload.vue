<template>
  <div class="image-upload">
    <el-upload
      v-model:file-list="fileList"
      class="upload-demo"
      :action="uploadUrl"
      :before-upload="handleBeforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-remove="handleRemove"
      :limit="1"
      list-type="picture"
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
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadProps, UploadUserFile } from 'element-plus'

const props = defineProps<{
  value?: string
}>()

const emit = defineEmits<{
  'update:value': [value: string]
}>()

const uploadUrl = '/api/upload/image'
const fileList = ref<UploadUserFile[]>([])

// 监听 value 变化，更新文件列表
watch(() => props.value, (newValue) => {
  if (newValue && !fileList.value.length) {
    fileList.value = [{
      name: 'Current Image',
      url: newValue
    }]
  }
}, { immediate: true })

const handleBeforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

const handleSuccess: UploadProps['onSuccess'] = (response) => {
  if (response.code === 0 && response.data?.url) {
    emit('update:value', response.data.url)
    ElMessage.success('上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

const handleError: UploadProps['onError'] = () => {
  ElMessage.error('上传失败')
}

const handleRemove = () => {
  emit('update:value', '')
}
</script>

<style scoped>
.image-upload {
  width: 100%;
}

:deep(.el-upload-list--picture) {
  margin-top: 10px;
}
</style> 