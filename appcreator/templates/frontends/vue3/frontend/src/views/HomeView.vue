<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { Button } from '@/components/ui/button'
import { APP_NAME, ASSISTANT_NAMES } from '@/config'
import { api } from '@/services/api'

interface HealthResponse {
  status: string
  app_name: string
  environment: string
  version: string
}

const backendStatus = ref<'checking' | 'connected' | 'disconnected'>('checking')
const backendInfo = ref<HealthResponse | null>(null)

async function checkBackend(): Promise<void> {
  backendStatus.value = 'checking'
  try {
    const res = await api.get<HealthResponse>('/health')
    backendInfo.value = res.data
    backendStatus.value = 'connected'
  } catch {
    backendInfo.value = null
    backendStatus.value = 'disconnected'
  }
}

const skills = [
  { name: '/init-project', text: 'Omgeving controleren' },
  { name: '/brainstorm-architect', text: 'Ontwerpsessie' },
  { name: '/feature-builder', text: 'Bouwen per plak' },
]

onMounted(checkBackend)
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-8 py-6">
    <section class="bg-card space-y-4 rounded-xl border p-8 shadow-sm">
      <p class="bg-primary/10 text-primary inline-flex rounded-full px-3 py-1 text-xs font-medium">
        AppCreator boilerplate
      </p>
      <h1 class="text-foreground text-3xl font-extrabold">Welkom bij {{ APP_NAME }}</h1>
      <p class="text-muted-foreground max-w-2xl text-base leading-relaxed">
        Je Vue 3 frontend en FastAPI backend zijn geconfigureerd. Gebruik {{ ASSISTANT_NAMES }} om verder te bouwen met
        de meegeleverde AI-skills.
      </p>
    </section>

    <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
      <section class="bg-card space-y-4 rounded-xl border p-6">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold">Backend API-status</h2>
          <span
            v-if="backendStatus === 'connected'"
            data-testid="backend-status"
            class="bg-success/10 text-success rounded-full px-2.5 py-0.5 text-xs font-medium"
          >
            Verbonden
          </span>
          <span
            v-else-if="backendStatus === 'checking'"
            data-testid="backend-status"
            class="bg-muted text-muted-foreground rounded-full px-2.5 py-0.5 text-xs font-medium"
          >
            Controleren…
          </span>
          <span
            v-else
            data-testid="backend-status"
            class="bg-destructive/10 text-destructive rounded-full px-2.5 py-0.5 text-xs font-medium"
          >
            Niet bereikbaar
          </span>
        </div>
        <p class="text-muted-foreground text-sm">
          Controleert de verbinding met
          <code class="bg-muted rounded px-1.5 py-0.5 font-mono text-xs">/api/v1/health</code>.
        </p>
        <Button variant="secondary" size="sm" @click="checkBackend">Opnieuw testen</Button>
      </section>

      <section class="bg-card space-y-4 rounded-xl border p-6">
        <h2 class="text-lg font-semibold">AI-skills</h2>
        <p class="text-muted-foreground text-sm">Start in de chat van {{ ASSISTANT_NAMES }}:</p>
        <ul class="space-y-2 font-mono text-xs">
          <li
            v-for="skill in skills"
            :key="skill.name"
            class="bg-muted/50 flex items-center justify-between rounded p-2"
          >
            <span class="text-primary font-bold">{{ skill.name }}</span>
            <span class="text-muted-foreground">{{ skill.text }}</span>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>
