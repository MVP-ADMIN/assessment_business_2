export default {
  path: '/refunds',
  component: () => import('@/layouts/default.vue'),
  meta: { title: '返款管理' },
  children: [
    {
      path: '',
      name: 'RefundList',
      component: () => import('@/views/refunds/index.vue'),
      meta: { title: '返款列表' }
    },
    {
      path: 'create',
      name: 'CreateRefund',
      component: () => import('@/views/refunds/CreateRefund.vue'),
      meta: { title: '新建返款' }
    },
    {
      path: ':id',
      name: 'RefundDetail',
      component: () => import('@/views/refunds/RefundDetail.vue'),
      meta: { title: '返款详情' }
    },
    {
      path: ':id/payments/create',
      name: 'CreatePayment',
      component: () => import('@/views/refunds/CreatePayment.vue'),
      meta: { title: '创建支付记录' }
    }
  ]
} 