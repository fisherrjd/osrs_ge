<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'

const router = useRouter()

function goHome() {
  router.push('/')
}

function handleLogin() {
  // Placeholder for future login functionality
  console.log('Login clicked')
}

function handleLatestNews() {
  console.log('Latest News clicked')
}

function handleAIHub() {
  console.log('AI Hub clicked')
}

function handlePortfolio() {
  console.log('Portfolio clicked')
}
</script>

<template>
  <nav class="border-b-4 border-accent bg-card">
    <div class="container mx-auto px-4 py-4">
      <div class="flex items-center justify-between">
        <!-- Logo / Brand -->
        <div class="flex items-center gap-3 cursor-pointer" @click="goHome">
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
          </div>
        </div>

        <!-- Right side - Live indicator and Navigation buttons -->
        <div class="flex items-center gap-6">
          <Button
            @click="handleLatestNews"
            variant="outline"
            class="border-accent text-accent hover:bg-accent hover:text-accent-foreground"
          >
            Latest News
          </Button>

          <Button
            @click="handleAIHub"
            variant="outline"
            class="border-accent text-accent hover:bg-accent hover:text-accent-foreground"
          >
            AI Hub
          </Button>

          <Button
            @click="handlePortfolio"
            variant="outline"
            class="border-accent text-accent hover:bg-accent hover:text-accent-foreground"
          >
            Investments
          </Button>
        </div>
      </div>
    </div>
  </nav>
</template>
