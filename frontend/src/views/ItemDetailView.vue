<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Item } from '@/types/item'
import { Button } from '@/components/ui/button'

const route = useRoute()
const router = useRouter()
const item = ref<Item | null>(null)
const loading = ref(true)

function getIconUrl(icon: string): string {
  return `https://oldschool.runescape.wiki/images/${icon.replace(/ /g, '_')}`
}

function getMembershipIcon(members: boolean): string {
  return members
    ? 'https://oldschool.runescape.wiki/images/Member_icon.png'
    : 'https://oldschool.runescape.wiki/images/Free-to-play_icon.png'
}

function goBack() {
  router.push('/')
}

async function fetchItem() {
  loading.value = true
  try {
    const itemId = route.params.id
    const response = await fetch(`https://osrs.jade.rip/api/items?skip=0&limit=100`)
    const data = await response.json()
    item.value = data.items.find((i: Item) => i.id === Number(itemId)) || null
  } catch (error) {
    console.error('Failed to fetch item:', error)
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
    <div class="mb-6">
      <Button
        @click="goBack"
        variant="outline"
        class="border-accent text-accent hover:bg-accent hover:text-accent-foreground"
      >
        ← Back to Items
      </Button>
    </div>

    <div v-if="loading" class="text-center py-8 text-secondary">Loading...</div>

    <div v-else-if="item" class="space-y-6">
      <!-- Item Header -->
      <div class="bg-card rounded-lg border border-border p-6">
        <div class="flex items-center gap-4">
          <img :src="getIconUrl(item.icon)" :alt="item.name" class="w-16 h-16" />
          <div>
            <div class="flex items-center gap-3 mb-2">
              <h1 class="text-3xl font-bold text-primary">{{ item.name }}</h1>
              <img
                :src="getMembershipIcon(item.members)"
                :alt="item.members ? 'Members' : 'Free-to-play'"
                class="w-5 h-5"
                :title="item.members ? 'Members only' : 'Free-to-play'"
              />
            </div>
            <p class="text-muted-foreground">{{ item.examine }}</p>
          </div>
        </div>
      </div>

      <!-- Price Chart Placeholder -->
      <div class="bg-card rounded-lg border border-border p-6">
        <h2 class="text-xl font-semibold text-accent mb-4">Price History</h2>
        <div class="h-96 flex items-center justify-center border-2 border-dashed border-border rounded">
          <p class="text-muted-foreground">Chart will go here</p>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-8 text-secondary">Item not found</div>
  </div>
</template>
