---
name: vue-shadcn
description: "Werkwijze voor de Vue 3-frontend met Shadcn-Vue: componenten installeren en gebruiken, formulieren met validatie en het thema aanpassen. Gebruik bij elk werk aan schermen of componenten in frontend/src."
---

# Vue-shadcn

## Componenten installeren

Shadcn-Vue-componenten worden als broncode in het project gezet, in `frontend/src/components/ui/`. Kijk eerst of het component daar al staat.

```bash
cd frontend

# Eén component
npx shadcn-vue@latest add button

# Meerdere tegelijk
npx shadcn-vue@latest add card dialog input table
```

De instellingen staan in `frontend/components.json`. De geïnstalleerde bestanden zijn van het project: pas ze aan als het ontwerp daarom vraagt.

## Een component gebruiken

```vue
<script setup lang="ts">
import { Plus } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const emit = defineEmits<{
  create: []
}>()
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Overzicht</CardTitle>
      <CardDescription>Beheer je actieve records</CardDescription>
    </CardHeader>
    <CardContent>
      <Button class="gap-2" @click="emit('create')">
        <Plus class="h-4 w-4" />
        Nieuw toevoegen
      </Button>
    </CardContent>
  </Card>
</template>
```

- Importeer componenten uit `@/components/ui/<component>` en iconen uit `@lucide/vue`.
- Voeg voorwaardelijke classes samen met `cn()` uit `@/lib/utils`: `:class="cn('rounded-lg border', isActive && 'border-primary')"`.

## Formulieren

Installeer eerst de formuliercomponenten (`npx shadcn-vue@latest add form input`). Leg de validatie vast in een Zod-schema:

```ts
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import * as z from 'zod'

const formSchema = toTypedSchema(
  z.object({
    name: z.string().min(2, 'Minimaal 2 tekens'),
    email: z.string().email('Ongeldig e-mailadres'),
  }),
)

const form = useForm({ validationSchema: formSchema })

const onSubmit = form.handleSubmit(async (values) => {
  // values is getypeerd volgens het schema
})
```

Toon fouten van de API ook in het formulier, niet alleen de validatie in de browser.

## Thema

De kleuren zijn CSS-variabelen in `frontend/src/assets/index.css` (`--primary`, `--background`, `--card`, `--radius`). Pas het thema daar aan en gebruik in componenten de bijbehorende classes zoals `bg-primary` en `text-muted-foreground`. Vaste kleuren zoals `bg-blue-500` volgen het thema en de donkere modus niet.

## Data ophalen

Haal data op via `api` uit `@/services/api` en gebruik de gegenereerde types uit `frontend/src/types/`. Toon bij elke aanroep een laadstatus en een foutmelding.

## Controleren

```bash
cd frontend && npm run lint && npm run build
```
