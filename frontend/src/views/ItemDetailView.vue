<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Item } from '@/types/item'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatRelativeTime } from '@/lib/utils'

const route = useRoute()
const router = useRouter()
const item = ref<Item | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

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

function getMembershipText(members: boolean): string {
  return members ? 'Members' : 'Free-to-play'
}

function goBack() {
  router.push('/')
}

async function fetchItem() {
  loading.value = true
  error.value = null
  try {
    const itemId = route.params.id
    const response = await fetch(`https://osrs.jade.rip/api/items/${itemId}`)

    if (!response.ok) {
      if (response.status === 404) {
        error.value = 'Item not found'
      } else {
        error.value = 'Failed to fetch item'
      }
      return
    }

    item.value = await response.json()
  } catch (err) {
    console.error('Failed to fetch item:', err)
    error.value = 'Failed to fetch item'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchItem()
})
</script>

<template>
  <div>
    <!-- Header -->
    <header class="border-b-4 border-accent bg-card mb-6">
      <div class="container mx-auto py-4 px-4">
        <div class="flex items-center gap-4">
          <Button
            @click="goBack"
            variant="outline"
            class="border-accent text-accent hover:bg-accent hover:text-accent-foreground"
          >
            ← Back
          </Button>
          <h1 class="text-2xl font-bold flex items-center gap-3">
            <span class="text-primary">Item Details</span>
          </h1>
        </div>
      </div>
    </header>

    <div class="container mx-auto px-4 pb-8">
      <div v-if="loading" class="text-center py-8 text-secondary">Loading...</div>

      <div v-else-if="error" class="text-center py-8">
        <p class="text-destructive mb-4">{{ error }}</p>
        <Button
          @click="goBack"
          variant="outline"
          class="border-accent text-accent hover:bg-accent hover:text-accent-foreground"
        >
          Return to Items
        </Button>
      </div>

      <div v-else-if="item" class="space-y-6">
        <!-- Item Header Card -->
        <Card>
          <CardContent class="pt-6">
            <div class="flex items-start gap-6">
              <img :src="getIconUrl(item.icon)" :alt="item.name" class="w-20 h-20" />
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <h1 class="text-3xl font-bold text-primary">{{ item.name }}</h1>
                  <img
                    :src="getMembershipIcon(item.members)"
                    :alt="getMembershipText(item.members)"
                    class="w-6 h-6"
                    :title="getMembershipText(item.members)"
                  />
                </div>
                <p class="text-muted-foreground mb-4">{{ item.examine }}</p>
                <div class="flex gap-4 text-sm">
                  <div>
                    <span class="text-muted-foreground">Item ID:</span>
                    <span class="ml-2 text-secondary font-medium">{{ item.id }}</span>
                  </div>
                  <div>
                    <span class="text-muted-foreground">Membership:</span>
                    <span class="ml-2 text-secondary font-medium">{{
                      getMembershipText(item.members)
                    }}</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

<!-- Current Prices Grid - Compact -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <!-- Buy Price Card -->
          <Card>
            <CardContent class="pt-4 pb-3">
              <div class="text-xs text-muted-foreground mb-1">Buy Price</div>
              <div class="text-xl font-bold text-primary">{{ formatGold(item.high) }}</div>
              <div class="text-xs text-muted-foreground mt-1">
                {{ formatRelativeTime(item.highTime) }}
              </div>
            </CardContent>
          </Card>

          <!-- Sell Price Card -->
          <Card>
            <CardContent class="pt-4 pb-3">
              <div class="text-xs text-muted-foreground mb-1">Sell Price</div>
              <div class="text-xl font-bold text-primary">{{ formatGold(item.low) }}</div>
              <div class="text-xs text-muted-foreground mt-1">
                {{ formatRelativeTime(item.lowTime) }}
              </div>
            </CardContent>
          </Card>

          <!-- Margin Card -->
          <Card>
            <CardContent class="pt-4 pb-3">
              <div class="text-xs text-muted-foreground mb-1">Margin</div>
              <div class="text-xl font-bold text-primary">{{ formatGold(item.margin) }}</div>
              <div class="text-xs text-muted-foreground mt-1">After tax</div>
            </CardContent>
          </Card>

          <!-- Volume Card -->
          <Card>
            <CardContent class="pt-4 pb-3">
              <div class="text-xs text-muted-foreground mb-1">Volume (24h)</div>
              <div class="text-xl font-bold text-primary">{{ item.volume_24h.toLocaleString() }}</div>
              <div class="text-xs text-muted-foreground mt-1">Items traded</div>
            </CardContent>
          </Card>
        </div>
<!-- Trading Information Card -->
        <Card>
          <CardHeader>
            <CardTitle class="text-accent">Trading Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div>
                <div class="text-sm text-muted-foreground mb-1">ROI per Item</div>
                <div class="text-2xl font-bold text-primary">
                  {{
                    item.low && item.low > 0
                      ? ((item.margin / item.low) * 100).toFixed(2) + '%'
                      : 'N/A'
                  }}
                </div>
              </div>
              <div>
                <div class="text-sm text-muted-foreground mb-1">Max Daily Profit</div>
                <div class="text-2xl font-bold text-primary">
                  {{ item.limit ? formatGold(item.margin * item.limit) : 'N/A' }}
                </div>
              </div>
              <div>
                <div class="text-sm text-muted-foreground mb-1">Tax per Item</div>
                <div class="text-2xl font-bold text-primary">
                  {{
                    item.high
                      ? formatGold(Math.floor(item.high * 0.01))
                      : 'N/A'
                  }}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        <!-- Price Chart Placeholder -->
        <Card>
          <CardHeader>
            <CardTitle class="text-accent">Price History</CardTitle>
          </CardHeader>
          <CardContent>
            <div
              class="h-96 flex items-center justify-center border-2 border-dashed border-border rounded"
            >
              <p class="text-muted-foreground">Chart will go here</p>
            </div>
          </CardContent>
        </Card>

        <!-- Item Details Card -->
        <Card>
          <CardHeader>
            <CardTitle class="text-accent">Item Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-3">
                <div class="flex justify-between py-2 border-b border-border">
                  <span class="text-muted-foreground">Buy Limit:</span>
                  <span class="text-secondary font-medium">{{ item.limit || 'N/A' }}</span>
                </div>
                <div class="flex justify-between py-2 border-b border-border">
                  <span class="text-muted-foreground">High Alch:</span>
                  <span class="text-secondary font-medium">{{ formatGold(item.highalch) }}</span>
                </div>
                <div class="flex justify-between py-2 border-b border-border">
                  <span class="text-muted-foreground">Low Alch:</span>
                  <span class="text-secondary font-medium">{{ formatGold(item.lowalch) }}</span>
                </div>
              </div>
              <div class="space-y-3">
                <div class="flex justify-between py-2 border-b border-border">
                  <span class="text-muted-foreground">Store Value:</span>
                  <span class="text-secondary font-medium">{{ formatGold(item.value) }}</span>
                </div>
                <div class="flex justify-between py-2 border-b border-border">
                  <span class="text-muted-foreground">Icon URL:</span>
                  <a
                    :href="item.icon_url"
                    target="_blank"
                    class="text-accent hover:underline text-sm truncate max-w-[200px] inline-block"
                    >{{ item.icon }}</a
                  >
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
