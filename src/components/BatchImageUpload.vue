<template>
  <div class="batch-upload">
    <el-upload
      class="upload-component"
      :action="`${baseUrl}/api/upload/images`"
      :headers="headers"
      name="files[]"
      :before-upload="beforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-exceed="handleExceed"
      :limit="20"
      multiple
      :show-file-list="true"
      list-type="picture"
      :file-list="fileList"
      :on-remove="handleRemove"
      drag
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处，或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持jpg/png格式，单个文件不超过2MB，最多可上传20张
        </div>
      </template>
    </el-upload>

    <div class="upload-info" v-if="uploadedCount > 0">
      <el-progress
        :percentage="uploadProgress"
        :format="progressFormat"
        :status="uploadProgress === 100 ? 'success' : ''"
      />
      <div class="upload-stats">
        已上传: {{ uploadedCount }}/{{ totalFiles }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { UploadProps, UploadUserFile } from 'element-plus'

const props = defineProps<{
  modelValue: string[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
}>()

const baseUrl = import.meta.env.VITE_API_URL
const headers = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

const fileList = ref<UploadUserFile[]>([])
const uploadedCount = ref(0)
const totalFiles = ref(0)

const uploadProgress = computed(() => {
  if (totalFiles.value === 0) return 0
  return Math.round((uploadedCount.value / totalFiles.value) * 100)
})

const progressFormat = (percentage: number) => {
  return percentage === 100 ? '上传完成' : `${percentage}%`
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

const handleSuccess: UploadProps['onSuccess'] = (response, uploadFile) => {
  if (response.code === 0) {
    uploadedCount.value++
    emit('update:modelValue', [...props.modelValue, response.data.url])
    ElMessage.success('上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

const handleError: UploadProps['onError'] = () => {
  ElMessage.error('上传失败')
}

const handleExceed = () => {
  ElMessage.warning('最多只能上传20个文件')
}

const handleRemove = (file: UploadUserFile) => {
  const index = props.modelValue.findIndex(url => url.includes(file.name))
  if (index > -1) {
    const newUrls = [...props.modelValue]
    newUrls.splice(index, 1)
    emit('update:modelValue', newUrls)
  }
  uploadedCount.value = Math.max(0, uploadedCount.value - 1)
}
</script>

<style scoped>
.batch-upload {
  padding: 20px;
}

.upload-component {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  padding: 20px;
  text-align: center;
  background-color: var(--el-bg-color-page);
}

.upload-info {
  margin-top: 20px;
}

.upload-stats {
  margin-top: 10px;
  color: var(--el-text-color-secondary);
}

:deep(.el-upload-list) {
  margin-top: 16px;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

.el-upload__text {
  margin-top: 10px;
  color: var(--el-text-color-regular);
}

.el-upload__text em {
  color: var(--el-color-primary);
  font-style: normal;
}
</style> 