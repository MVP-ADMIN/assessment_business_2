import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://192.168.1.20:5000',
  timeout: 10000
})

request.interceptors.response.use(
  response => {
    const res = response.data

    // 处理特殊的历史记录接口
    if (response.config.url?.includes('/history')) {
      if (res.code === 0) {
        return res
      }
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }

    // 处理其他接口
    if (response.config.url === '/api/options') {
      return res
    }

    if (response.status === 201 || response.status === 200) {
      if (res.code === 0 || !res.code) {
        return res.data || res
      }
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }

    return res
  },
  error => {
    console.error('API Error:', error)
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request 