<script setup lang="ts">
/** The **?** link to the help article of the current screen (`meta.help` of the route); hidden without one. */
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { CircleHelp } from '@lucide/vue'

import { Button } from '@/components/ui/button'

const route = useRoute()

const target = computed(() => {
  const [category, slug] = (route.meta.help ?? '').split('/')
  if (!category || !slug) return null
  return { name: 'help-article', params: { category, slug } }
})
</script>

<template>
  <Button v-if="target" as-child variant="ghost" size="icon">
    <RouterLink :to="target" data-testid="help-button" aria-label="Hulp bij dit scherm" title="Hulp bij dit scherm">
      <CircleHelp aria-hidden="true" />
    </RouterLink>
  </Button>
</template>
