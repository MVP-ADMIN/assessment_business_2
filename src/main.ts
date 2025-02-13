import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
// 先导入 ElementPlus 的样式
import 'element-plus/dist/index.css'
// 再导入自定义样式
import './styles/main.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { createPinia } from 'pinia'
import axios from './utils/axios'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(router)
app.use(ElementPlus)
app.use(createPinia())

// 全局配置 axios
app.config.globalProperties.$axios = axios

// 挂载应用
app.mount('#app') 