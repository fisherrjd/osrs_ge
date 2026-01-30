// Item Type Definition
//
export interface Item {
  id: number
  name: string
  examine: string
  icon_url: string
  members: boolean
  lowalch: number
  limit: number
  value: number
  highalch: number
  icon: string
  high: number | null
  highTime: number | null
  low: number | null
  lowTime: number | null
  volume_24h: number
  margin: number
}

// History API Types
export type HistoryPeriod = '1d' | '1w' | '1m' | '6m'

export interface HistoryDataPoint {
  timestamp: string
  avg_high_price: number | null
  avg_low_price: number | null
  high_price_volume: number | null
  low_price_volume: number | null
  total_volume: number | null
}

export interface ItemHistoryResponse {
  item_id: number
  item_name: string
  period: HistoryPeriod
  resolution: string
  count: number
  data: HistoryDataPoint[]
}
