<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import type { Item } from '@/types/item'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { formatRelativeTime } from '@/lib/utils'

const items = ref<Item[]>([])
const loading = ref(true)
const total = ref(0)
const hasMore = ref(false)
const lastUpdated = ref<Date | null>(null)
let pollInterval: ReturnType<typeof setInterval> | null = null

// Filter states
const searchQuery = ref('')
const minMargin = ref<number | ''>('')
const minVolume = ref<number | ''>('')
const membersFilter = ref<'all' | 'members' | 'f2p'>('all')
const maxTimeAgo = ref<number | ''>('')

// Pagination states
const currentPage = ref(0)
const itemsPerPage = 15

// Sorting states
const sortBy = ref('volume_24h')
const sortOrder = ref<'asc' | 'desc'>('desc')

function formatGold(value: number | null): string {
  if (value === null) return '-'
  return value.toLocaleString() + ' gp'
}

function getIconUrl(icon: string): string {
  return `https://oldschool.runescape.wiki/images/${icon.replace(/ /g, '_')}`
}

function getMembershipIcon(members: boolean): string {
  return members
    ? 'https://oldschool.runescape.wiki/images/Member_icon.png'
    : 'https://oldschool.runescape.wiki/images/Free-to-play_icon.png'
}

async function fetchItems(showLoading = true) {
  if (showLoading) loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('skip', String(currentPage.value * itemsPerPage))
    params.append('limit', String(itemsPerPage))
    params.append('sort_by', sortBy.value)
    params.append('sort_order', sortOrder.value)

    if (searchQuery.value) {
      params.append('name', searchQuery.value)
    }

    if (minMargin.value !== '') {
      params.append('min_margin', String(minMargin.value))
    }

    if (minVolume.value !== '') {
      params.append('min_volume', String(minVolume.value))
    }

    if (membersFilter.value !== 'all') {
      params.append('members', String(membersFilter.value === 'members'))
    }

    if (maxTimeAgo.value !== '') {
      params.append('max_time_ago', String(maxTimeAgo.value))
    }

    const response = await fetch(`https://osrs.jade.rip/api/items?${params}`)
    const data = await response.json()
    items.value = data.items
    total.value = data.total
    hasMore.value = data.has_more
    lastUpdated.value = new Date()
  } catch (error) {
    console.error('Failed to fetch items:', error)
  } finally {
    loading.value = false
  }
}

function silentRefresh() {
  fetchItems(false)
}

function nextPage() {
  if (hasMore.value) {
    currentPage.value++
    fetchItems()
  }
}

function previousPage() {
  if (currentPage.value > 0) {
    currentPage.value--
    fetchItems()
  }
}

function resetFilters() {
  searchQuery.value = ''
  minMargin.value = ''
  minVolume.value = ''
  membersFilter.value = 'all'
  maxTimeAgo.value = ''
  currentPage.value = 0
}

function applyFilters() {
  currentPage.value = 0
  fetchItems()
}

function toggleSort(column: string) {
  if (sortBy.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortOrder.value = 'desc'
  }
  currentPage.value = 0
  fetchItems()
}

function getSortIcon(column: string): string {
  if (sortBy.value !== column) return '↕'
  return sortOrder.value === 'asc' ? '↑' : '↓'
}

// Watch for filter changes and apply them
watch([searchQuery, minMargin, minVolume, membersFilter, maxTimeAgo], () => {
  applyFilters()
})

// Polling setup - refresh every 60 seconds
onMounted(() => {
  fetchItems()
  pollInterval = setInterval(silentRefresh, 60000)
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<template>
  <div class="min-h-screen">
    <!-- Header with green accent border -->
    <header class="border-b-4 border-accent bg-card mb-6">
      <div class="container mx-auto py-4 px-4 flex items-center justify-between">
        <h1 class="text-2xl font-bold flex items-center gap-3">
          <span class="text-primary">Varlamore Terminal</span>
          <span
            class="text-xs font-semibold px-2 py-1 rounded bg-secondary text-secondary-foreground"
            >VT</span
          >
        </h1>
        <div class="flex items-center gap-2 text-sm text-muted-foreground">
          <span class="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
          <span>Live</span>
          <span v-if="lastUpdated" class="text-xs"
            >· Updated {{ formatRelativeTime(Math.floor(lastUpdated.getTime() / 1000)) }}</span
          >
        </div>
      </div>
    </header>

    <div class="container mx-auto px-4 pb-8">
      <!-- Filters -->
      <div class="mb-6 space-y-4 p-4 bg-card rounded-lg border border-border">
        <div class="flex gap-4 flex-wrap">
          <div class="flex-1 min-w-[200px]">
            <label class="text-sm font-medium mb-2 block text-secondary">Search Items</label>
            <Input v-model="searchQuery" placeholder="Search by name..." class="w-full" />
          </div>

          <div class="w-[180px]">
            <label class="text-sm font-medium mb-2 block text-secondary">Min Margin (GP)</label>
            <Input
              v-model.number="minMargin"
              type="number"
              placeholder="e.g. 100000"
              class="w-full"
            />
          </div>

          <div class="w-[180px]">
            <label class="text-sm font-medium mb-2 block text-secondary">Min Volume (24h)</label>
            <Input
              v-model.number="minVolume"
              type="number"
              placeholder="e.g. 1000"
              class="w-full"
            />
          </div>

          <div class="w-[180px]">
            <label class="text-sm font-medium mb-2 block text-secondary">Membership</label>
            <select
              v-model="membersFilter"
              class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
            >
              <option value="all">All Items</option>
              <option value="members">Members Only</option>
              <option value="f2p">F2P Only</option>
            </select>
          </div>

          <div class="w-[180px]">
            <label class="text-sm font-medium mb-2 block text-secondary">Max Time Ago</label>
            <select
              v-model.number="maxTimeAgo"
              class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
            >
              <option value="">Any time</option>
              <option :value="5">5 minutes</option>
              <option :value="15">15 minutes</option>
              <option :value="30">30 minutes</option>
              <option :value="60">1 hour</option>
              <option :value="180">3 hours</option>
              <option :value="360">6 hours</option>
              <option :value="720">12 hours</option>
              <option :value="1440">24 hours</option>
            </select>
          </div>

          <div class="flex items-end">
            <Button
              @click="resetFilters"
              variant="outline"
              class="border-accent text-accent hover:bg-accent hover:text-accent-foreground"
              >Reset</Button
            >
          </div>
        </div>

        <div class="text-sm text-muted-foreground">
          Showing
          <span class="text-secondary font-medium"
            >{{ currentPage * itemsPerPage + 1 }}-{{
              Math.min((currentPage + 1) * itemsPerPage, total)
            }}</span
          >
          of <span class="text-secondary font-medium">{{ total.toLocaleString() }}</span> items
        </div>
      </div>

      <div v-if="loading" class="text-center py-8 text-secondary">Loading...</div>

      <div v-else class="bg-card rounded-lg border border-border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow class="bg-accent/10 hover:bg-accent/10">
              <TableHead class="text-accent font-semibold">Item</TableHead>
              <TableHead
                class="text-right cursor-pointer hover:bg-accent/20 text-accent font-semibold"
                @click="toggleSort('high')"
              >
                Buy Price {{ getSortIcon('high') }}
              </TableHead>
              <TableHead class="text-right text-accent font-semibold">Buy Time</TableHead>
              <TableHead
                class="text-right cursor-pointer hover:bg-accent/20 text-accent font-semibold"
                @click="toggleSort('low')"
              >
                Sell Price {{ getSortIcon('low') }}
              </TableHead>
              <TableHead class="text-right text-accent font-semibold">Sell Time</TableHead>
              <TableHead
                class="text-right cursor-pointer hover:bg-accent/20 text-accent font-semibold"
                @click="toggleSort('margin')"
              >
                Margin {{ getSortIcon('margin') }}
              </TableHead>
              <TableHead
                class="text-right cursor-pointer hover:bg-accent/20 text-accent font-semibold"
                @click="toggleSort('volume_24h')"
              >
                Volume (24h) {{ getSortIcon('volume_24h') }}
              </TableHead>
              <TableHead class="text-right text-accent font-semibold">Buy Limit</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="item in items" :key="item.id" class="hover:bg-accent/5">
              <TableCell class="font-medium">
                <div class="flex items-center gap-3">
                  <img :src="getIconUrl(item.icon)" :alt="item.name" class="w-8 h-8" />
                  <span>{{ item.name }}</span>
                  <img
                    :src="getMembershipIcon(item.members)"
                    :alt="item.members ? 'Members' : 'Free-to-play'"
                    class="w-4 h-4"
                    :title="item.members ? 'Members only' : 'Free-to-play'"
                  />
                </div>
              </TableCell>
              <TableCell class="text-right text-secondary">{{ formatGold(item.high) }}</TableCell>
              <TableCell class="text-right text-muted-foreground text-sm">{{
                formatRelativeTime(item.highTime)
              }}</TableCell>
              <TableCell class="text-right text-secondary">{{ formatGold(item.low) }}</TableCell>
              <TableCell class="text-right text-muted-foreground text-sm">{{
                formatRelativeTime(item.lowTime)
              }}</TableCell>
              <TableCell class="text-right font-medium text-secondary">{{
                formatGold(item.margin)
              }}</TableCell>
              <TableCell class="text-right">{{ item.volume_24h.toLocaleString() }}</TableCell>
              <TableCell class="text-right">{{ item.limit || '-' }}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>

      <!-- Pagination -->
      <div class="mt-6 flex items-center justify-between">
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
          <span class="text-secondary font-medium">{{ Math.ceil(total / itemsPerPage) }}</span>
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
  </div>
</template>

<style scoped></style>
