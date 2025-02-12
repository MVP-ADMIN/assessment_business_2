import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/default.vue'),
    children: [
      {
        path: '',
        redirect: '/demands'
      },
      {
        path: 'demands',
        name: 'Demands',
        component: () => import('@/views/demands/index.vue'),
        meta: { 
          requiresAuth: true,
          title: '需求管理'
        }
      },
      {
        path: 'demands/create',
        name: 'CreateDemand',
        component: () => import('@/views/demands/CreateDemand.vue'),
        meta: { title: '创建需求' }
      },
      {
        path: 'demands/:id',
        name: 'DemandDetail',
        component: () => import('@/views/demands/DemandDetail.vue'),
        props: true,
        meta: { requiresAuth: true }
      },
      {
        path: 'demands/:id/edit',
        name: 'EditDemand',
        component: () => import('@/views/demands/EditDemand.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'demands/:demandId/details/create',
        name: 'CreateDetail',
        component: () => import('@/views/demands/CreateDetail.vue'),
        meta: { title: '新增测评明细' }
      },
      {
        path: 'demands/:demandId/details/:detailId',
        name: 'DetailView',
        component: () => import('@/views/demands/DetailView.vue'),
        meta: { title: '测评明细详情' }
      },
      {
        path: 'demands/:demandId/details/:detailId/edit',
        name: 'EditDetail',
        component: () => import('@/views/demands/EditDetail.vue'),
        meta: { title: '编辑测评明细' }
      },
      {
        path: 'refunds',
        name: 'Refunds',
        component: () => import('@/views/refunds/index.vue'),
        meta: { 
          requiresAuth: true,
          title: '返款管理'
        }
      },
      {
        path: 'refunds/create-payment',
        name: 'CreatePayment',
        component: () => import('@/views/refunds/CreatePayment.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'orders/create',
        name: 'CreateRefundOrder',
        component: () => import('@/views/refunds/CreateOrder.vue'),
        meta: { title: '录入订单明细' }
      },
      {
        path: 'reviews/create',
        name: 'CreateRefundReview',
        component: () => import('@/views/refunds/CreateReview.vue'),
        meta: { title: '录入评价明细' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})


export default router 