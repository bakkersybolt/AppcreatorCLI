<script setup lang="ts">
import { RouterView } from 'vue-router'

import { Toaster } from '@/components/ui/sonner'
import { APP_NAME } from '@/config'
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <header class="border-b px-6 py-4">
      <h1 class="text-xl font-bold">{{ APP_NAME }}</h1>
    </header>

    <main class="flex-1 p-6">
      <RouterView />
    </main>

    <!-- The one toaster of the app: `toast.success(...)` / `useApiError().showError(...)` from any screen. -->
    <Toaster position="top-center" />
  </div>
</template>
