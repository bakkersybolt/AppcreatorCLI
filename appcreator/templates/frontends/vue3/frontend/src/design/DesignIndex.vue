<script setup lang="ts">
/** Design sandbox (`/_ontwerp`, development only): the list of sandbox screens. */
import { RouterLink } from 'vue-router'

import { designScreens } from './screens'
</script>

<template>
  <div class="mx-auto flex max-w-3xl flex-col gap-6 py-2">
    <header class="flex flex-col gap-1">
      <p class="text-primary text-xs font-semibold tracking-wide uppercase">Alleen in ontwikkeling</p>
      <h1 class="text-2xl font-bold">Ontwerp</h1>
      <p class="text-muted-foreground">
        Schermen met vaste voorbeelddata, om de uitstraling te bekijken op 390 en 1280 px breed.
      </p>
    </header>

    <ul class="flex flex-col gap-3" data-testid="design-screens">
      <li v-for="screen in designScreens" :key="screen.key">
        <RouterLink
          :to="{ name: 'design-screen', params: { scherm: screen.key } }"
          class="bg-card hover:border-primary/50 flex flex-col gap-1 rounded-xl border p-4"
        >
          <span class="font-semibold">{{ screen.title }}</span>
          <span class="text-muted-foreground text-sm">{{ screen.description }}</span>
        </RouterLink>
      </li>
    </ul>
  </div>
</template>
