import type { Demand } from './demand'
import type { DemandDetail } from './detail'

// 返款记录
export interface RefundRecord {
  id: number
  demand_id: number          // 关联需求ID
  detail_id: number          // 关联测评明细ID
  marketing_number: string   // 来自需求表
  order_number: string       // 来自测评明细表
  amount: number
  currency: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  create_time: string
  demand?: Demand           // 关联的需求信息
  detail?: DemandDetail     // 关联的测评明细
}

// 订单明细
export interface RefundOrder {
  id: number
  demand_id: number          // 关联需求ID
  detail_id: number          // 关联测评明细ID
  marketing_number: string   // 来自需求表
  dingtalk_number: string    // 来自需求表
  asin: string              // 来自需求表
  intermediary: string      // 来自需求表的中介信息
  order_number: string      // 来自测评明细表
  order_date: string        // 来自测评明细表
  order_amount: number      // 来自测评明细表
  currency: string
  review_type: string       // 关联评价类型
  business_type: 'joint' | 'self'
  brand: string            // 来自需求表
  payment_method: string
  paypal_principal: number
  rmb_commission: number
  intermediary_commission: number
  commission_currency: 'USD' | 'CNY'
  exchange_rate: number
  actual_payment: number
  demand?: Demand          // 关联的需求信息
  detail?: DemandDetail    // 关联的测评明细
}

// 评价明细
export interface RefundReview {
  id: number
  order_id: number         // 关联返款订单ID
  detail_id: number        // 关联测评明细ID
  review_type: string      // 与测评明细的评价类型关联
  review_link: string      // 与测评明细的评价链接关联
  remark: string
  screenshot1: string      // 与测评明细的评价截图关联
  screenshot2: string      // 与测评明细的评价截图关联
  detail?: DemandDetail    // 关联的测评明细
  refund_order?: RefundOrder // 关联的返款订单
}

// 返款明细
export interface RefundPayment {
  id: number
  order_id: number         // 关联返款订单ID
  detail_id: number        // 关联测评明细ID
  customer_email: string
  order_amount: number     // 来自测评明细表
  transfer_amount: number
  currency: string
  intermediary_commission: number
  commission_currency: string
  rmb_commission: number
  payment_method: string
  payment_account: string
  payment_time: string
  remark: string
  detail?: DemandDetail    // 关联的测评明细
  refund_order?: RefundOrder // 关联的返款订单
}

// 返款状态变更记录
export interface RefundStatusLog {
  id: number
  order_id: number
  old_status: string
  new_status: string
  change_time: string
  change_reason: string
  operator: string
}

// 汇率记录
export interface ExchangeRate {
  id: number
  currency_from: string
  currency_to: string
  rate: number
  update_time: string
} 