<script setup lang="ts">
import { ref } from 'vue'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

type NewsCategory = 'all' | 'official' | 'reddit' | 'updates'

const activeTab = ref<NewsCategory>('all')

interface NewsItem {
  id: number
  title: string
  description: string
  source: 'official' | 'reddit'
  category: 'update' | 'patch' | 'community' | 'event'
  date: string
  timeAgo: string
  url: string
  upvotes?: number
  comments?: number
}

const dummyNews: NewsItem[] = [
  {
    id: 1,
    title: 'Varlamore: The Rising Kingdom - Part 2',
    description: 'Continue your journey through the ancient kingdom of Varlamore. New quests, bosses, and rewards await brave adventurers in this second major content update.',
    source: 'official',
    category: 'update',
    date: '2024-01-24',
    timeAgo: '2 hours ago',
    url: 'https://secure.runescape.com/m=news/varlamore-the-rising-kingdom-part-2',
  },
  {
    id: 2,
    title: 'Game Update - January 24th 2024',
    description: 'This week sees various quality of life improvements, bug fixes, and balancing changes based on community feedback.',
    source: 'official',
    category: 'patch',
    date: '2024-01-24',
    timeAgo: '5 hours ago',
    url: 'https://secure.runescape.com/m=news/game-update-january-24th-2024',
  },
  {
    id: 3,
    title: 'Finally hit 99 Runecrafting after 3 years of playing',
    description: 'Started playing in 2021 and finally got my first 99. The grind was real but worth it. Here are some tips for anyone else going for it.',
    source: 'reddit',
    category: 'community',
    date: '2024-01-24',
    timeAgo: '1 hour ago',
    url: 'https://www.reddit.com/r/2007scape/comments/example1',
    upvotes: 2847,
    comments: 342,
  },
]

function openNewsItem(url: string) {
  window.open(url, '_blank', 'noopener,noreferrer')
}

const tabs: { key: NewsCategory; label: string }[] = [
  { key: 'all', label: 'All News' },
  { key: 'official', label: 'Official' },
  { key: 'reddit', label: 'Reddit' },
  { key: 'updates', label: 'Game Updates' },
]

function filteredNews() {
  if (activeTab.value === 'all') return dummyNews
  if (activeTab.value === 'official') return dummyNews.filter(n => n.source === 'official')
  if (activeTab.value === 'reddit') return dummyNews.filter(n => n.source === 'reddit')
  if (activeTab.value === 'updates') return dummyNews.filter(n => n.category === 'update' || n.category === 'patch')
  return dummyNews
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
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </Button>
    </div>

    <!-- News Grid -->
    <div class="grid gap-4">
      <Card
        v-for="item in filteredNews()"
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
            <span class="text-xs text-muted-foreground whitespace-nowrap">{{ item.timeAgo }}</span>
          </div>
        </CardHeader>
        <CardContent>
          <CardDescription class="text-sm leading-relaxed">
            {{ item.description }}
          </CardDescription>

          <!-- Reddit-specific stats -->
          <div v-if="item.source === 'reddit'" class="flex items-center gap-4 mt-4 text-sm text-muted-foreground">
            <span class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              </svg>
              {{ item.upvotes?.toLocaleString() }}
            </span>
            <span class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              {{ item.comments }}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Empty State -->
    <div v-if="filteredNews().length === 0" class="text-center py-12">
      <p class="text-muted-foreground">No news items found for this filter.</p>
    </div>
  </div>
</template>
