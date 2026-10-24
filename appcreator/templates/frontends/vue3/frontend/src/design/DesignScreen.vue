<script setup lang="ts">
/** One sandbox screen (`/_ontwerp/:scherm`), in a frame of a chosen width (phone 390 px, desktop 1280 px). */
import { computed, defineAsyncComponent, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ArrowLeft } from '@lucide/vue'

import { Button } from '@/components/ui/button'
import { designScreens } from './screens'

const route = useRoute()
const screen = computed(() => designScreens.find((s) => s.key === route.params.scherm))
const view = computed(() => (screen.value ? defineAsyncComponent(screen.value.component) : null))

const WIDTHS = [
  { label: '390 px', value: '390px' },
  { label: '1280 px', value: '1280px' },
  { label: 'Vol', value: '100%' },
]
const width = ref('100%')
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <RouterLink
        :to="{ name: 'design' }"
        class="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-sm"
      >
        <ArrowLeft class="size-4" aria-hidden="true" />
        Alle ontwerpschermen
      </RouterLink>
      <div v-if="screen" class="flex gap-2" role="group" aria-label="Breedte">
        <Button
          v-for="option in WIDTHS"
          :key="option.value"
          size="sm"
          :variant="width === option.value ? 'default' : 'outline'"
          :aria-pressed="width === option.value"
          @click="width = option.value"
        >
          {{ option.label }}
        </Button>
      </div>
    </div>

    <div
      v-if="view"
      data-testid="design-frame"
      class="mx-auto w-full overflow-x-auto rounded-xl border border-dashed p-4"
      :style="{ maxWidth: width }"
    >
      <component :is="view" />
    </div>
    <p v-else data-testid="design-not-found" class="text-muted-foreground">
      Dit ontwerpscherm bestaat niet. Kies er een uit de lijst.
    </p>
  </div>
</template>
