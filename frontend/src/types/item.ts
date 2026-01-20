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
