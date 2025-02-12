export interface Demand {
  demand_id: number
  marketing_number: string
  dingtalk_number: string
  asin: string
  assessment_quantity: number
  text_review_quantity: number
  image_review_quantity: number
  video_review_quantity: number
  product_price: number
  search_keyword: string
  hyperlink: string
  other_notes: string
  status_id: number
  status_name: string
  ordered_quantity: number
  unordered_quantity: number
  reviewed_quantity: number
  unreviewed_quantity: number
  registration_date: string
  first_order_date: string
}

export interface DemandForm {
  marketing_number: string
  dingtalk_number: string
  asin: string
  assessment_quantity: number
  text_review_quantity: number
  image_review_quantity: number
  video_review_quantity: number
  product_price: number | null
  search_keyword: string
  hyperlink: string
  other_notes: string
  status_id: number
  model_id: number
  type_id: number
  platform_id: number
  country_id: number
  brand_id: number
  store_id: number
  account_id: number
  method_id: number
  ad_entry_option_id: number
  variant_option_id: number
  free_review_quantity: number
  like_only_quantity: number
  fb_order_quantity: number
  ordered_quantity: number
  unordered_quantity: number
  reviewed_quantity: number
  unreviewed_quantity: number
  registration_date: string | null
  first_order_date: string | null
  product_image_url: string
  received_product_image_url: string
  order_style: string
  attribute_value_1: string
  attribute_value_2: string
  intermediary_id?: number | null
  intermediary_status?: number
  intermediary_remark?: string
  assignment_time?: string | null
  completion_time?: string | null
  payment_amount?: number | null
  payment_time?: string | null
  payment_status?: number
}

export interface DemandListItem extends DemandForm {
  id: number
  created_at: string
  updated_at: string
}

export interface SelectOption {
  label: string
  value: number
}

export interface StatusOption {
  status_id: number
  status_name: string
}

export interface ModelOption {
  model_id: number
  model_name: string
}

export interface TypeOption {
  type_id: number
  type_name: string
}

export interface PlatformOption {
  platform_id: number
  platform_name: string
}

export interface CountryOption {
  country_id: number
  country_name: string
}

export interface BrandOption {
  brand_id: number
  brand_name: string
}

export interface StoreOption {
  store_id: number
  store_name: string
}

export interface AccountOption {
  account_id: number
  account_name: string
}

export interface MethodOption {
  method_id: number
  method_name: string
}

export interface AdEntryOption {
  option_id: number
  option_name: string
}

export interface VariantOption {
  option_id: number
  option_name: string
}

export interface Intermediary {
  id: number
  name: string
}

export interface IntermediaryStatus {
  status_id: number
  status_name: string
}

export interface PaymentStatus {
  status_id: number
  status_name: string
} 