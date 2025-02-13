import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  timeout: 10000
})

request.interceptors.response.use(
  response => {
    if (response.config.url === '/api/options') {
      return response.data
    }

    if (response.status === 201 || response.status === 200) {
      const res = response.data
      if (res.code === 0 || !res.code) {
        return res.data || res
      }
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }

    return response.data
  },
  error => {
    console.error('API Error:', error)
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request 