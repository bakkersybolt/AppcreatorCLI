<script setup lang="ts">
/**
 * Sandbox example screen: the current look built from the real components with fixed data (no API, no store).
 * The skill `design-system` adjusts this screen after every change of tokens or building blocks.
 */
import { CircleCheck, Info } from '@lucide/vue'

import FormAlert from '@/components/common/FormAlert.vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

/** Colour tokens as Tailwind classes; the values live in `src/assets/brand/tokens.css`. */
const SWATCHES = [
  { name: 'primary', class: 'bg-primary text-primary-foreground' },
  { name: 'secondary', class: 'bg-secondary text-secondary-foreground' },
  { name: 'accent', class: 'bg-accent text-accent-foreground' },
  { name: 'muted', class: 'bg-muted text-muted-foreground' },
  { name: 'success', class: 'bg-success text-success-foreground' },
  { name: 'warning', class: 'bg-warning text-warning-foreground' },
  { name: 'destructive', class: 'bg-destructive text-primary-foreground' },
]

/** Fixed example data: only here in the sandbox, never in a real view. */
const ITEMS = [
  { id: 1, title: 'Eerste voorbeeld', meta: 'Gewijzigd op 12 maart', done: true },
  { id: 2, title: 'Tweede voorbeeld met een wat langere naam', meta: 'Gewijzigd op 3 april', done: false },
  { id: 3, title: 'Derde voorbeeld', meta: 'Nieuw', done: false },
]
</script>

<template>
  <div class="flex flex-col gap-8" data-testid="voorbeeld-scherm">
    <header class="flex flex-col gap-1">
      <p class="text-primary text-xs font-semibold tracking-wide uppercase">Voorbeeld</p>
      <h1 class="text-3xl font-bold">Koptekst van een scherm</h1>
      <p class="text-muted-foreground max-w-prose">
        Een gewone alinea in de bodytekst. Zo ziet lopende tekst eruit, met voldoende regelafstand om prettig te lezen.
      </p>
    </header>

    <section class="flex flex-col gap-3">
      <h2 class="text-lg font-semibold">Kleuren</h2>
      <ul class="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <li v-for="swatch in SWATCHES" :key="swatch.name" :class="[swatch.class, 'rounded-lg border p-3 text-sm']">
          {{ swatch.name }}
        </li>
      </ul>
    </section>

    <section class="flex flex-col gap-3">
      <h2 class="text-lg font-semibold">Knoppen</h2>
      <div class="flex flex-wrap gap-2">
        <Button>Opslaan</Button>
        <Button variant="secondary">Secundair</Button>
        <Button variant="outline">Annuleren</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="destructive">Verwijderen</Button>
        <Button disabled>Opslaan…</Button>
      </div>
    </section>

    <div class="grid gap-6 md:grid-cols-2">
      <section class="bg-card flex flex-col gap-4 rounded-xl border p-5">
        <h2 class="text-lg font-semibold">Formulier</h2>
        <div class="flex flex-col gap-2">
          <Label for="voorbeeld-naam">Naam</Label>
          <Input id="voorbeeld-naam" model-value="Een ingevulde waarde" />
        </div>
        <div class="flex flex-col gap-2">
          <Label for="voorbeeld-fout">Veld met een fout</Label>
          <Input id="voorbeeld-fout" aria-invalid="true" model-value="" />
          <p class="text-destructive text-sm">Vul dit veld in.</p>
        </div>
        <FormAlert>Je gegevens konden niet worden opgeslagen. Probeer het later opnieuw.</FormAlert>
        <Button class="self-start">Opslaan</Button>
      </section>

      <section class="bg-card flex flex-col gap-3 rounded-xl border p-5">
        <h2 class="text-lg font-semibold">Lijst</h2>
        <ul class="flex flex-col">
          <li v-for="item in ITEMS" :key="item.id" class="hover:bg-muted flex items-center gap-3 rounded-lg px-2 py-2">
            <CircleCheck
              :class="['size-5 shrink-0', item.done ? 'text-success' : 'text-muted-foreground']"
              aria-hidden="true"
            />
            <div class="min-w-0 flex-1">
              <p class="truncate font-medium">{{ item.title }}</p>
              <p class="text-muted-foreground text-sm">{{ item.meta }}</p>
            </div>
          </li>
        </ul>
        <Alert>
          <Info aria-hidden="true" />
          <AlertTitle>Goed om te weten</AlertTitle>
          <AlertDescription>Een melding binnen een kaart, voor informatie die niet dringend is.</AlertDescription>
        </Alert>
      </section>
    </div>
  </div>
</template>
