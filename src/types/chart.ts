export interface StatusChartData {
  name: string
  value: number
}

export interface ProgressChartData {
  date: string
  total: number
  completed: number
}

export interface ReviewChartData {
  type: 'text' | 'image' | 'video'
  count: number
}

export interface StatsData {
  status: StatusChartData[]
  progress: ProgressChartData[]
  reviews: ReviewChartData[]
} 