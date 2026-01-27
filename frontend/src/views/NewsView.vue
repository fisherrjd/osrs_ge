<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

type NewsCategory = 'all' | 'official' | 'reddit' | 'updates'

const activeTab = ref<NewsCategory>('all')
const loading = ref(true)
const currentPage = ref(0)
const itemsPerPage = 10

interface NewsItem {
  id: number
  title: string
  description: string | null
  source: 'official' | 'reddit'
  category: 'update' | 'patch' | 'community' | 'event'
  date: string
  url: string
  upvotes?: number | null
  comments?: number | null
  score: number
}

const newsItems = ref<NewsItem[]>([])

async function fetchNews() {
  loading.value = true
  try {
    const response = await fetch('https://osrs.jade.rip/api/news')
    newsItems.value = await response.json()
  } catch (error) {
    console.error('Failed to fetch news:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchNews()
})

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const secondsAgo = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (secondsAgo < 60) return 'Just now'

  const minutesAgo = Math.floor(secondsAgo / 60)
  if (minutesAgo < 60) return `${minutesAgo} minute${minutesAgo !== 1 ? 's' : ''} ago`

  const hoursAgo = Math.floor(minutesAgo / 60)
  if (hoursAgo < 24) return `${hoursAgo} hour${hoursAgo !== 1 ? 's' : ''} ago`

  const daysAgo = Math.floor(hoursAgo / 24)
  if (daysAgo < 30) return `${daysAgo} day${daysAgo !== 1 ? 's' : ''} ago`

  const monthsAgo = Math.floor(daysAgo / 30)
  return `${monthsAgo} month${monthsAgo !== 1 ? 's' : ''} ago`
}

function openNewsItem(url: string) {
  window.open(url, '_blank', 'noopener,noreferrer')
}

const tabs: { key: NewsCategory; label: string }[] = [
  { key: 'all', label: 'All News' },
  { key: 'official', label: 'Official' },
  { key: 'reddit', label: 'Reddit' },
  { key: 'updates', label: 'Game Updates' },
]

const filteredNews = computed(() => {
  let filtered = newsItems.value
  if (activeTab.value === 'official') {
    filtered = newsItems.value.filter(n => n.source === 'official')
  } else if (activeTab.value === 'reddit') {
    filtered = newsItems.value.filter(n => n.source === 'reddit')
  } else if (activeTab.value === 'updates') {
    filtered = newsItems.value.filter(n => n.category === 'update' || n.category === 'patch')
  }
  return filtered
})

const paginatedNews = computed(() => {
  const start = currentPage.value * itemsPerPage
  return filteredNews.value.slice(start, start + itemsPerPage)
})

const totalPages = computed(() => Math.ceil(filteredNews.value.length / itemsPerPage))
const hasMore = computed(() => currentPage.value < totalPages.value - 1)

function nextPage() {
  if (hasMore.value) currentPage.value++
}

function previousPage() {
  if (currentPage.value > 0) currentPage.value--
}

function onTabChange(tab: NewsCategory) {
  activeTab.value = tab
  currentPage.value = 0
}

function getCategoryBadgeVariant(category: NewsItem['category']): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (category) {
    case 'update': return 'default'
    case 'patch': return 'secondary'
    case 'event': return 'destructive'
    case 'community': return 'outline'
    default: return 'outline'
  }
}

function formatCategory(category: NewsItem['category']): string {
  return category.charAt(0).toUpperCase() + category.slice(1)
}
</script>

<template>
  <div class="container mx-auto px-4 py-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-primary mb-2">News</h1>
      <p class="text-muted-foreground">Latest updates from OSRS and the community</p>
    </div>

    <!-- Tab Navigation -->
    <div class="flex gap-2 mb-6 border-b border-border pb-4">
      <Button
        v-for="tab in tabs"
        :key="tab.key"
        :variant="activeTab === tab.key ? 'default' : 'ghost'"
        :class="[
          activeTab === tab.key
            ? 'bg-accent text-accent-foreground'
            : 'text-muted-foreground hover:text-foreground'
        ]"
        @click="onTabChange(tab.key)"
      >
        {{ tab.label }}
      </Button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8 text-secondary">Loading...</div>

    <!-- News Grid -->
    <div v-else class="grid gap-4">
      <Card
        v-for="item in paginatedNews"
        :key="item.id"
        class="hover:border-accent/50 transition-colors cursor-pointer"
        @click="openNewsItem(item.url)"
      >
        <CardHeader class="pb-3">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <Badge :variant="getCategoryBadgeVariant(item.category)">
                  {{ formatCategory(item.category) }}
                </Badge>
                <Badge variant="outline" :class="item.source === 'official' ? 'border-accent text-accent' : 'border-orange-500 text-orange-500'">
                  {{ item.source === 'official' ? 'Jagex' : 'Reddit' }}
                </Badge>
              </div>
              <CardTitle class="text-lg leading-tight">{{ item.title }}</CardTitle>
            </div>
            <span class="text-xs text-muted-foreground whitespace-nowrap">{{ formatTimeAgo(item.date) }}</span>
          </div>
        </CardHeader>
        <CardContent>
          <CardDescription class="text-sm leading-relaxed">
            {{ item.description }}
          </CardDescription>

          <!-- Reddit-specific stats -->
          <div v-if="item.source === 'reddit' && item.upvotes" class="flex items-center gap-4 mt-4 text-sm text-muted-foreground">
            <span class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              </svg>
              {{ item.upvotes?.toLocaleString() }}
            </span>
            <span v-if="item.comments" class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              {{ item.comments }}
            </span>
          </div>
        </CardContent>
      </Card>

      <!-- Empty State -->
      <div v-if="paginatedNews.length === 0" class="text-center py-12">
        <p class="text-muted-foreground">No news items found for this filter.</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && filteredNews.length > 0" class="mt-6 flex items-center justify-between">
      <Button
        @click="previousPage"
        :disabled="currentPage === 0"
        variant="outline"
        class="border-accent text-accent hover:bg-accent hover:text-accent-foreground disabled:opacity-50"
      >
        Previous
      </Button>

      <div class="text-sm text-muted-foreground">
        Page <span class="text-secondary font-medium">{{ currentPage + 1 }}</span> of
        <span class="text-secondary font-medium">{{ totalPages }}</span>
        (<span class="text-secondary font-medium">{{ filteredNews.length }}</span> items)
      </div>

      <Button
        @click="nextPage"
        :disabled="!hasMore"
        variant="outline"
        class="border-accent text-accent hover:bg-accent hover:text-accent-foreground disabled:opacity-50"
      >
        Next
      </Button>
    </div>
  </div>
</template>
