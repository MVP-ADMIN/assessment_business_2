<template>
  <div class="video-upload">
    <el-upload
      v-model:file-list="fileList"
      class="upload-demo"
      :action="uploadUrl"
      :before-upload="handleBeforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-remove="handleRemove"
      :limit="1"
      :accept="acceptTypes"
    >
      <template #trigger>
        <el-button type="primary">选择视频</el-button>
      </template>
      <template #tip>
        <div class="el-upload__tip">
          只能上传 mp4/webm 视频文件，且不超过 50MB
        </div>
      </template>
    </el-upload>

    <div v-if="value" class="video-preview">
      <video :src="value" controls class="preview-video" />
    </div>
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

const uploadUrl = '/api/upload/video'
const fileList = ref<UploadUserFile[]>([])
const acceptTypes = '.mp4,.webm'

// 监听 value 变化，更新文件列表
watch(() => props.value, (newValue) => {
  if (newValue && !fileList.value.length) {
    fileList.value = [{
      name: 'Current Video',
      url: newValue
    }]
  }
}, { immediate: true })

const handleBeforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isVideo = file.type.startsWith('video/')
  const isLt50M = file.size / 1024 / 1024 < 50

  if (!isVideo) {
    ElMessage.error('只能上传视频文件!')
    return false
  }
  if (!isLt50M) {
    ElMessage.error('视频大小不能超过 50MB!')
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
.video-upload {
  width: 100%;
}

.video-preview {
  margin-top: 10px;
}

.preview-video {
  max-width: 100%;
  max-height: 200px;
  border-radius: 4px;
}

:deep(.el-upload-list) {
  margin-top: 10px;
}
</style> 