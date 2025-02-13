export interface DemandDetail {
  detail_id: number
  demand_id: number
  order_number: string
  order_amount: number
  order_time: string
  review_time: string | null
  review_content: string | null
  review_images: string[]
  review_video: string | null
  payment_screenshot: string | null
  order_screenshot: string | null
  review_screenshot: string | null
  status: number
  status_name: string
  remark: string | null
  created_at: string
  updated_at: string
}

export const DetailStatus = {
  PENDING: 1,     // 待处理
  ORDERED: 2,     // 已下单
  REVIEWED: 3,    // 已评价
  CANCELLED: 4,   // 已取消
} as const

export interface DemandDetailForm {
  demand_id: number
  order_number: string
  order_amount: number
  order_time: string
  review_content: string
  review_time: string | null
  review_images: string[]
  review_video: string
  payment_screenshot: string
  order_screenshot: string
  review_screenshot: string
  status: number
  remark: string
} 