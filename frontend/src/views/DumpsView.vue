<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

interface DumpEvent {
  id: number
  item_id: number
  item_name: string
  event_type: 'dump' | 'spike'
  detected_at: string
  trigger_price: number
  baseline_price: number
  price_change_percent: number
  trigger_volume: number
  baseline_volume: number
  volume_change_percent: number
}

const router = useRouter()
const events = ref<DumpEvent[]>([])
const loading = ref(true)
const total = ref(0)
const hasMore = ref(false)
let pollInterval: ReturnType<typeof setInterval> | null = null

// Filter state
const eventTypeFilter = ref<'all' | 'dump' | 'spike'>('all')
const hoursAgoFilter = ref<number | ''>('')

// Pagination
const currentPage = ref(0)
const eventsPerPage = 20

function formatPrice(value: number): string {
  if (value >= 1_000_000_000) {
    return (value / 1_000_000_000).toFixed(2) + 'b'
  }
  if (value >= 1_000_000) {
    return (value / 1_000_000).toFixed(2) + 'm'
  }
  if (value >= 1_000) {
    return Math.floor(value / 1_000) + 'k'
  }
  return value.toLocaleString()
}

function formatPercent(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(1)}%`
}

function formatTime(isoString: string): string {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`

  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}

function navigateToItem(itemId: number) {
  router.push(`/item/${itemId}`)
}

async function fetchEvents(showLoading = true) {
  if (showLoading) loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('skip', String(currentPage.value * eventsPerPage))
    params.append('limit', String(eventsPerPage))

    if (eventTypeFilter.value !== 'all') {
      params.append('event_type', eventTypeFilter.value)
    }

    if (hoursAgoFilter.value !== '') {
      params.append('hours_ago', String(hoursAgoFilter.value))
    }

    const response = await fetch(`https://osrs.jade.rip/api/dumps?${params}`)
    const data = await response.json()
    events.value = data.events
    total.value = data.total
    hasMore.value = data.has_more
  } catch (error) {
    console.error('Failed to fetch events:', error)
  } finally {
    loading.value = false
  }
}

function silentRefresh() {
  fetchEvents(false)
}

function nextPage() {
  if (hasMore.value) {
    currentPage.value++
    fetchEvents()
  }
}

function previousPage() {
  if (currentPage.value > 0) {
    currentPage.value--
    fetchEvents()
  }
}

function applyFilters() {
  currentPage.value = 0
  fetchEvents()
}

// Watch for filter changes
watch([eventTypeFilter, hoursAgoFilter], () => {
  applyFilters()
})

// Polling - refresh every 60 seconds
onMounted(() => {
  fetchEvents()
  pollInterval = setInterval(silentRefresh, 60000)
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<template>
  <div class="container mx-auto px-4 py-6 pb-8">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-primary mb-2">Dump & Spike Tracker</h1>
      <p class="text-muted-foreground">
        Real-time detection of significant price movements with volume spikes.
      </p>
    </div>

    <!-- Filters -->
    <div class="mb-6 p-4 bg-card rounded-lg border border-border">
      <div class="flex gap-4 flex-wrap items-end">
        <div class="w-[180px]">
          <label class="text-sm font-medium mb-2 block text-secondary">Event Type</label>
          <select
            v-model="eventTypeFilter"
            class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
          >
            <option value="all">All Events</option>
            <option value="dump">Dumps Only</option>
            <option value="spike">Spikes Only</option>
          </select>
        </div>

        <div class="w-[180px]">
          <label class="text-sm font-medium mb-2 block text-secondary">Time Range</label>
          <select
            v-model.number="hoursAgoFilter"
            class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
          >
            <option value="">All Time</option>
            <option :value="1">Last Hour</option>
            <option :value="6">Last 6 Hours</option>
            <option :value="24">Last 24 Hours</option>
            <option :value="72">Last 3 Days</option>
            <option :value="168">Last Week</option>
          </select>
        </div>

        <div class="text-sm text-muted-foreground self-center">
          <span class="text-secondary font-medium">{{ total }}</span> events found
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center py-8 text-secondary">Loading...</div>

    <!-- Empty state -->
    <div
      v-else-if="events.length === 0"
      class="bg-card rounded-lg border border-border p-8 text-center"
    >
      <p class="text-muted-foreground">No dump or spike events detected yet.</p>
      <p class="text-sm text-muted-foreground mt-2">
        Events are detected when price changes ≥5% with volume ≥2x average.
      </p>
    </div>

    <!-- Events table -->
    <div v-else class="bg-card rounded-lg border border-border overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow class="bg-accent/10 hover:bg-accent/10">
            <TableHead class="text-accent font-semibold">Time</TableHead>
            <TableHead class="text-accent font-semibold">Item</TableHead>
            <TableHead class="text-accent font-semibold">Type</TableHead>
            <TableHead class="text-right text-accent font-semibold">Price Change</TableHead>
            <TableHead class="text-right text-accent font-semibold">Volume Change</TableHead>
            <TableHead class="text-right text-accent font-semibold">Trigger Price</TableHead>
            <TableHead class="text-right text-accent font-semibold">Baseline</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow
            v-for="event in events"
            :key="event.id"
            class="hover:bg-accent/5 cursor-pointer"
            @click="navigateToItem(event.item_id)"
          >
            <TableCell class="text-muted-foreground">
              {{ formatTime(event.detected_at) }}
            </TableCell>
            <TableCell class="font-medium">
              {{ event.item_name }}
            </TableCell>
            <TableCell>
              <Badge
                :variant="event.event_type === 'dump' ? 'destructive' : 'default'"
                :class="event.event_type === 'spike' ? 'bg-green-600 hover:bg-green-700' : ''"
              >
                {{ event.event_type === 'dump' ? '↓ Dump' : '↑ Spike' }}
              </Badge>
            </TableCell>
            <TableCell
              class="text-right font-medium"
              :class="event.price_change_percent < 0 ? 'text-red-500' : 'text-green-500'"
            >
              {{ formatPercent(event.price_change_percent) }}
            </TableCell>
            <TableCell class="text-right text-secondary">
              {{ formatPercent(event.volume_change_percent) }}
            </TableCell>
            <TableCell class="text-right"> {{ formatPrice(event.trigger_price) }} gp </TableCell>
            <TableCell class="text-right text-muted-foreground">
              {{ formatPrice(event.baseline_price) }} gp
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <!-- Pagination -->
    <div v-if="events.length > 0" class="mt-6 flex items-center justify-between">
      <Button
        @click="previousPage"
        :disabled="currentPage === 0 || loading"
        variant="outline"
        class="border-accent text-accent hover:bg-accent hover:text-accent-foreground disabled:opacity-50"
      >
        Previous
      </Button>

      <div class="text-sm text-muted-foreground">
        Page <span class="text-secondary font-medium">{{ currentPage + 1 }}</span> of
        <span class="text-secondary font-medium">{{ Math.ceil(total / eventsPerPage) || 1 }}</span>
      </div>

      <Button
        @click="nextPage"
        :disabled="!hasMore || loading"
        variant="outline"
        class="border-accent text-accent hover:bg-accent hover:text-accent-foreground disabled:opacity-50"
      >
        Next
      </Button>
    </div>
  </div>
</template>
