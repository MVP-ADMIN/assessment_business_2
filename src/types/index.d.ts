declare module 'vue' {
  import { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'vue-router' {
  import { RouteRecordRaw, Router } from 'vue-router'
  export { RouteRecordRaw, Router }
  export default Router
}

declare module 'element-plus' {
  import { ElMessage, ElMessageBox } from 'element-plus'
  export { ElMessage, ElMessageBox }
} 