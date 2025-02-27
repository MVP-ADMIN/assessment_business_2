import axios from 'axios'
import { ElMessage } from 'element-plus'
import { request } from 'http'

const request = axios.create({
  baseURL: 'http://192.168.1.20:5000',
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token 等认证信息
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response // 直接返回整个响应对象，在组件中处理数据
  },
  (error) => {
    console.error('API request failed:', error)
    ElMessage.error(error.response?.data?.message || error.message || '请求失败')
    return Promise.reject(error)
  }
)

export default request 