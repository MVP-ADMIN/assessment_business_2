import request from '@/utils/request'

export const uploadApi = {
  // 上传图片
  image: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/api/upload/image', formData)
  },
  
  // 上传多张图片
  images: (files: File[]) => {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files[]', file)
    })
    return request.post('/api/upload/images', formData)
  },
  
  // 上传视频
  video: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/api/upload/video', formData)
  }
} 