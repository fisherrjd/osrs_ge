<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Item } from '@/types/item'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

const items = ref<Item[]>([])
const loading = ref(true)

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

onMounted(async () => {
  try {
    const response = await fetch('https://osrs.jade.rip/api/items')
    const data = await response.json()
    items.value = data.items
  } catch (error) {
    console.error('Failed to fetch items:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="container mx-auto py-8">
    <h1 class="text-2xl font-bold mb-6">OSRS Grand Exchange</h1>

    <div v-if="loading" class="text-center py-8">Loading...</div>

    <Table v-else>
      <TableHeader>
        <TableRow>
          <TableHead>Item</TableHead>
          <TableHead class="text-right">Buy Price</TableHead>
          <TableHead class="text-right">Sell Price</TableHead>
          <TableHead class="text-right">Margin</TableHead>
          <TableHead class="text-right">Volume (24h)</TableHead>
          <TableHead class="text-right">Buy Limit</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="item in items" :key="item.id">
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
          <TableCell class="text-right">{{ formatGold(item.high) }}</TableCell>
          <TableCell class="text-right">{{ formatGold(item.low) }}</TableCell>
          <TableCell class="text-right">{{ formatGold(item.margin) }}</TableCell>
          <TableCell class="text-right">{{ item.volume_24h.toLocaleString() }}</TableCell>
          <TableCell class="text-right">{{ item.limit || '-' }}</TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>

<style scoped></style>
