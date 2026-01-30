<script setup lang="ts">
import { ref, watch, computed, shallowRef } from 'vue'
import { Line, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  type ChartData,
  type ChartOptions,
  type TooltipModel,
  type Chart,
} from 'chart.js'
import type { HistoryPeriod, ItemHistoryResponse } from '@/types/item'
import { Button } from '@/components/ui/button'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
)

const props = defineProps<{
  itemId: number
}>()

const periods: { value: HistoryPeriod; label: string }[] = [
  { value: '1d', label: '1D' },
  { value: '1w', label: '1W' },
  { value: '1m', label: '1M' },
  { value: '6m', label: '6M' },
]

const selectedPeriod = ref<HistoryPeriod>('1d')
const historyData = ref<ItemHistoryResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// Custom tooltip state
const tooltipVisible = ref(false)
const tooltipX = ref(0)
const tooltipY = ref(0)
const tooltipData = ref<{
  title: string
  buyPrice: string | null
  sellPrice: string | null
  buyVolume: string | null
  sellVolume: string | null
} | null>(null)

// Chart refs for crosshair sync
const priceChartRef = shallowRef<Chart | null>(null)
const volumeChartRef = shallowRef<Chart | null>(null)
const activeIndex = ref<number | null>(null)

function formatTimestamp(timestamp: string, period: HistoryPeriod): string {
  const date = new Date(timestamp)
  switch (period) {
    case '1d':
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    case '1w':
      return date.toLocaleDateString([], { weekday: 'short', hour: '2-digit' })
    case '1m':
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
    case '6m':
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
  }
}

function formatGold(value: number): string {
  if (value >= 1_000_000_000) {
    return (value / 1_000_000_000).toFixed(2) + 'B'
  }
  if (value >= 1_000_000) {
    return (value / 1_000_000).toFixed(2) + 'M'
  }
  if (value >= 1_000) {
    return (value / 1_000).toFixed(1) + 'K'
  }
  return value.toString()
}

function formatVolume(value: number): string {
  if (value >= 1_000_000) {
    return (value / 1_000_000).toFixed(1) + 'M'
  }
  if (value >= 1_000) {
    return (value / 1_000).toFixed(0) + 'K'
  }
  return value.toString()
}

// External tooltip handler
function externalTooltipHandler(context: { chart: Chart; tooltip: TooltipModel<'line' | 'bar'> }) {
  const { chart, tooltip } = context

  if (tooltip.opacity === 0) {
    tooltipVisible.value = false
    activeIndex.value = null
    return
  }

  const dataIndex = tooltip.dataPoints?.[0]?.dataIndex
  if (dataIndex === undefined || !historyData.value) return

  activeIndex.value = dataIndex
  const dataPoint = historyData.value.data[dataIndex]

  tooltipData.value = {
    title: tooltip.title[0] || '',
    buyPrice: dataPoint.avg_high_price ? formatGold(dataPoint.avg_high_price) + ' gp' : null,
    sellPrice: dataPoint.avg_low_price ? formatGold(dataPoint.avg_low_price) + ' gp' : null,
    buyVolume: dataPoint.high_price_volume ? formatVolume(dataPoint.high_price_volume) : null,
    sellVolume: dataPoint.low_price_volume ? formatVolume(dataPoint.low_price_volume) : null,
  }

  const position = chart.canvas.getBoundingClientRect()
  tooltipX.value = position.left + window.scrollX + tooltip.caretX
  tooltipY.value = position.top + window.scrollY + tooltip.caretY
  tooltipVisible.value = true
}

// Crosshair plugin
const crosshairLine = {
  id: 'crosshairLine',
  afterDraw(chart: Chart) {
    if (activeIndex.value === null) return

    const meta = chart.getDatasetMeta(0)
    if (!meta.data[activeIndex.value]) return

    const x = meta.data[activeIndex.value].x
    const ctx = chart.ctx
    const yAxis = chart.scales.y

    ctx.save()
    ctx.beginPath()
    ctx.moveTo(x, yAxis.top)
    ctx.lineTo(x, yAxis.bottom)
    ctx.lineWidth = 1
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.6)'
    ctx.setLineDash([4, 4])
    ctx.stroke()
    ctx.restore()
  },
}

const priceChartData = computed<ChartData<'line'>>(() => {
  if (!historyData.value || historyData.value.data.length === 0) {
    return { labels: [], datasets: [] }
  }

  const data = historyData.value.data
  const labels = data.map((d) => formatTimestamp(d.timestamp, selectedPeriod.value))

  return {
    labels,
    datasets: [
      {
        label: 'Buy Price',
        data: data.map((d) => d.avg_high_price),
        borderColor: 'rgb(34, 197, 94)',
        fill: false,
        tension: 0.3,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderWidth: 2,
      },
      {
        label: 'Sell Price',
        data: data.map((d) => d.avg_low_price),
        borderColor: 'rgb(239, 68, 68)',
        fill: false,
        tension: 0.3,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderWidth: 2,
      },
    ],
  }
})

const volumeChartData = computed<ChartData<'bar'>>(() => {
  if (!historyData.value || historyData.value.data.length === 0) {
    return { labels: [], datasets: [] }
  }

  const data = historyData.value.data
  const labels = data.map((d) => formatTimestamp(d.timestamp, selectedPeriod.value))

  return {
    labels,
    datasets: [
      {
        label: 'Buy Volume',
        data: data.map((d) => d.high_price_volume),
        backgroundColor: 'rgba(34, 197, 94, 0.6)',
        borderColor: 'rgba(34, 197, 94, 0.8)',
        borderWidth: 1,
        barPercentage: 0.9,
        categoryPercentage: 0.95,
      },
      {
        label: 'Sell Volume',
        data: data.map((d) => d.low_price_volume),
        backgroundColor: 'rgba(239, 68, 68, 0.6)',
        borderColor: 'rgba(239, 68, 68, 0.8)',
        borderWidth: 1,
        barPercentage: 0.9,
        categoryPercentage: 0.95,
      },
    ],
  }
})

const priceChartOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      enabled: false,
      external: externalTooltipHandler,
    },
  },
  scales: {
    x: {
      display: false,
    },
    y: {
      grid: {
        color: 'rgba(148, 163, 184, 0.3)',
      },
      ticks: {
        color: 'hsl(var(--muted-foreground))',
        callback: (value) => formatGold(value as number),
      },
    },
  },
}))

const volumeChartOptions = computed<ChartOptions<'bar'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      enabled: false,
      external: externalTooltipHandler,
    },
  },
  scales: {
    x: {
      grid: {
        color: 'rgba(148, 163, 184, 0.3)',
      },
      ticks: {
        color: 'hsl(var(--muted-foreground))',
        maxTicksLimit: 8,
      },
    },
    y: {
      grid: {
        color: 'rgba(148, 163, 184, 0.3)',
      },
      ticks: {
        color: 'hsl(var(--muted-foreground))',
        callback: (value) => formatVolume(value as number),
      },
    },
  },
}))

const priceChartPlugins = [crosshairLine]
const volumeChartPlugins = [crosshairLine]

async function fetchHistory() {
  loading.value = true
  error.value = null
  try {
    const response = await fetch(
      `https://osrs.jade.rip/api/items/${props.itemId}/history?period=${selectedPeriod.value}`,
    )
    if (!response.ok) {
      throw new Error('Failed to fetch history')
    }
    historyData.value = await response.json()
  } catch (err) {
    console.error('Failed to fetch history:', err)
    error.value = 'Failed to load price history'
  } finally {
    loading.value = false
  }
}

watch(selectedPeriod, () => {
  fetchHistory()
})

watch(
  () => props.itemId,
  () => {
    fetchHistory()
  },
  { immediate: true },
)

function handleChartMouseLeave() {
  tooltipVisible.value = false
  activeIndex.value = null
}
</script>

<template>
  <div class="space-y-4">
    <!-- Period Selector -->
    <div class="flex gap-2">
      <Button
        v-for="period in periods"
        :key="period.value"
        :variant="selectedPeriod === period.value ? 'default' : 'outline'"
        size="sm"
        @click="selectedPeriod = period.value"
        class="min-w-[3rem]"
      >
        {{ period.label }}
      </Button>
    </div>

    <!-- Charts Container -->
    <div class="relative" @mouseleave="handleChartMouseLeave">
      <div
        v-if="loading"
        class="absolute inset-0 flex items-center justify-center bg-background/50 z-10"
      >
        <span class="text-muted-foreground">Loading...</span>
      </div>

      <div v-else-if="error" class="h-96 flex items-center justify-center">
        <span class="text-destructive">{{ error }}</span>
      </div>

      <div
        v-else-if="!historyData || historyData.data.length === 0"
        class="h-96 flex items-center justify-center"
      >
        <span class="text-muted-foreground">No data available for this period</span>
      </div>

      <template v-else>
        <!-- Price Chart - 80% -->
        <div class="h-80">
          <Line :data="priceChartData" :options="priceChartOptions" :plugins="priceChartPlugins" />
        </div>
        <!-- Volume Chart - 20% -->
        <div class="h-20">
          <Bar
            :data="volumeChartData"
            :options="volumeChartOptions"
            :plugins="volumeChartPlugins"
          />
        </div>
      </template>

      <!-- Custom Tooltip -->
      <div
        v-if="tooltipVisible && tooltipData"
        class="fixed z-50 pointer-events-none px-3 py-2 rounded-lg shadow-lg border text-sm"
        :style="{
          left: tooltipX + 'px',
          top: tooltipY + 'px',
          transform: 'translate(-50%, -100%) translateY(-8px)',
          backgroundColor: 'rgba(30, 41, 59, 0.95)',
          borderColor: 'rgba(148, 163, 184, 0.3)',
          color: '#e2e8f0',
        }"
      >
        <div class="font-medium mb-1">{{ tooltipData.title }}</div>
        <div class="space-y-0.5 text-xs">
          <div class="flex justify-between gap-4">
            <span class="flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-green-500"></span>
              Buy:
            </span>
            <span>{{ tooltipData.buyPrice || '-' }}</span>
          </div>
          <div class="flex justify-between gap-4">
            <span class="flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-red-500"></span>
              Sell:
            </span>
            <span>{{ tooltipData.sellPrice || '-' }}</span>
          </div>
          <div class="border-t border-slate-600 my-1"></div>
          <div class="flex justify-between gap-4">
            <span class="flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-green-500/60"></span>
              Buy Vol:
            </span>
            <span>{{ tooltipData.buyVolume || '-' }}</span>
          </div>
          <div class="flex justify-between gap-4">
            <span class="flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-red-500/60"></span>
              Sell Vol:
            </span>
            <span>{{ tooltipData.sellVolume || '-' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Resolution Info -->
    <div v-if="historyData" class="text-xs text-muted-foreground text-right">
      Resolution: {{ historyData.resolution }} | {{ historyData.count }} data points
    </div>
  </div>
</template>
