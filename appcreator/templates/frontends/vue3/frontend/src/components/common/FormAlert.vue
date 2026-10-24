<script setup lang="ts">
import { AlertCircle } from '@lucide/vue'

/** General error of a form, above the submit button (`formError` of `useFormFeedback`): soft destructive block with icon. */
</script>

<template>
  <div
    data-slot="form-alert"
    role="alert"
    class="border-destructive/30 bg-destructive/10 text-destructive flex items-start gap-2 rounded-lg border p-3 text-sm"
  >
    <AlertCircle class="mt-0.5 size-4 shrink-0" aria-hidden="true" />
    <div class="min-w-0"><slot /></div>
  </div>
</template>
