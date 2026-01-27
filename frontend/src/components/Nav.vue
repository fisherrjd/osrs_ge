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

function handleNews() {
  router.push('/news')
}

function handleResearch() {
  router.push('/research')
}

function handlePortfolio() {
  router.push('/portfolio')
}

function handleDumps() {
  router.push('/dumps')
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
        </div>

        <!-- Center - Main Navigation -->
        <div class="flex items-center gap-2">

          <Button @click="handleNews" variant="ghost" class="text-foreground hover:bg-accent/50">
            News
          </Button>

          <Button
            @click="handleResearch"
            variant="ghost"
            class="text-foreground hover:bg-accent/50"
          >
            Research
          </Button>

          <Button
            @click="handlePortfolio"
            variant="ghost"
            class="text-foreground hover:bg-accent/50"
          >
            Portfolio
          </Button>

          <Button
            @click="handleDumps"
            variant="ghost"
            class="text-foreground hover:bg-accent/50"
          >
            Dumps
          </Button>
        </div>

        <!-- Right side - Live indicator and Login -->
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-2 text-sm text-muted-foreground">
            <span class="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
            <span>Live</span>
          </div>

          <Button
            @click="handleLogin"
            variant="outline"
            class="border-accent text-accent hover:bg-accent hover:text-accent-foreground"
          >
            Login
          </Button>
        </div>
      </div>
    </div>
  </nav>
</template>
