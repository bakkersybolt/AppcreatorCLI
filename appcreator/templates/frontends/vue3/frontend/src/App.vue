<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'

import HelpButton from '@/components/help/HelpButton.vue'
import { Toaster } from '@/components/ui/sonner'
import { APP_NAME } from '@/config'
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <header class="flex items-center justify-between gap-4 border-b px-6 py-4">
      <h1 class="text-xl font-bold">
        <RouterLink :to="{ name: 'home' }">{{ APP_NAME }}</RouterLink>
      </h1>
      <!-- Help of the current screen (`meta.help` in src/router/routes.ts). -->
      <HelpButton />
    </header>

    <main class="flex-1 p-6">
      <RouterView />
    </main>

    <!-- The one toaster of the app: `toast.success(...)` / `useApiError().showError(...)` from any screen. -->
    <Toaster position="top-center" />
  </div>
</template>
