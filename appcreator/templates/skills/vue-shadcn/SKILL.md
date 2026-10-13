---
name: vue-shadcn
description: "Praktische gids en best practices voor Vue 3, Shadcn-Vue componenten, Pinia state en Tailwind CSS."
---

# Skill: vue-shadcn

**Doel:** Praktische ondersteuning bieden bij het bouwen van moderne Vue 3 web interfaces met Shadcn-Vue en Tailwind CSS.

## Shadcn-Vue Componenten Toevoegen

Om componenten toe te voegen aan het project:
```bash
# Specifiek component toevoegen
npx shadcn-vue@latest add button

# Meerdere componenten tegelijk installeren
npx shadcn-vue@latest add button card dialog dropdown-menu input table tabs badge
```

## Aanbevolen Componentstructuur

Importeer geïnstalleerde Shadcn componenten altijd vanuit `@/components/ui/[component]`:

```vue
<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus } from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'create'): void
}>()
</script>

<template>
  <Card class="hover:shadow-md transition-shadow">
    <CardHeader>
      <CardTitle>Overzicht</CardTitle>
      <CardDescription>Beheer je actieve records</CardDescription>
    </CardHeader>
    <CardContent>
      <Button @click="emit('create')" class="gap-2">
        <Plus class="w-4 h-4" />
        Nieuw toevoegen
      </Button>
    </CardContent>
  </Card>
</template>
```

## Formulier Validatie (Vee-Validate + Zod)
Combineer Shadcn form componenten met Zod schema's:
```typescript
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import * as z from 'zod'

const formSchema = toTypedSchema(
  z.object({
    name: z.string().min(2, 'Minimaal 2 karakters'),
    email: z.string().email('Ongeldig e-mailadres'),
  })
)

const form = useForm({
  validationSchema: formSchema,
})
```
