import type { RouteRecordRaw } from 'vue-router'
import * as VueRouter from 'vue-router'
import request from '@/utils/request'

// 定义路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../layouts/BasicLayout.vue'),
    children: [
      {
        path: '',
        redirect: 'demands'
      },
      {
        path: 'demands',
        name: 'Demands',
        component: () => import('../views/demands/index.vue'),
        meta: { title: '需求管理' },
        beforeEnter: (to, from, next) => {
          request.get('/demands', { params: { page: 1, size: 20, keyword: '', status: '' } })
            .then(response => {
              // 处理响应
              next()
            })
            .catch(error => {
              // 处理错误
              next()
            })
        }
      },
      {
        path: 'demands/create',
        name: 'CreateDemand',
        component: () => import('../views/demands/CreateDemand.vue'),
        meta: { title: '创建需求' }
      },
      {
        path: 'demands/:id',
        name: 'DemandDetail',
        component: () => import('../views/demands/DemandDetail.vue'),
        meta: { title: '需求详情' }
      },
      {
        path: 'demands/:id/edit',
        name: 'EditDemand',
        component: () => import('../views/demands/EditDemand.vue'),
        meta: { title: '编辑需求' }
      },
      // 测评明细相关路由
      {
        path: 'demands/:demandId/details/create',
        name: 'CreateDetail',
        component: () => import('../views/demands/CreateDetail.vue'),
        meta: { title: '新增测评明细' }
      },
      {
        path: 'demands/:demandId/details/:detailId',
        name: 'DetailView',
        component: () => import('../views/demands/DetailView.vue'),
        meta: { title: '测评明细详情' }
      },
      {
        path: 'demands/:demandId/details/:detailId/edit',
        name: 'EditDetail',
        component: () => import('../views/demands/EditDetail.vue'),
        meta: { title: '编辑测评明细' }
      },
      // 返款相关路由
      {
        path: 'refunds',
        name: 'Refunds',
        component: () => import('../views/refunds/index.vue'),
        meta: { title: '返款管理' }
      },
      {
        path: 'refunds/create-payment',
        name: 'CreatePayment',
        component: () => import('../views/refunds/CreatePayment.vue'),
        meta: { title: '创建返款' }
      },
      {
        path: 'orders/create',
        name: 'CreateRefundOrder',
        component: () => import('../views/refunds/CreateOrder.vue'),
        meta: { title: '录入订单明细' }
      },
      {
        path: 'reviews/create',
        name: 'CreateRefundReview',
        component: () => import('../views/refunds/CreateReview.vue'),
        meta: { title: '录入评价明细' }
      }
    ]
  }
]

// 创建路由实例
const router = VueRouter.createRouter({
  history: VueRouter.createWebHistory(),
  routes
})

// 添加全局导航守卫，用于调试
router.beforeEach((to, from, next) => {
  console.log('Navigation to:', to.path)
  next()
})

export default router 