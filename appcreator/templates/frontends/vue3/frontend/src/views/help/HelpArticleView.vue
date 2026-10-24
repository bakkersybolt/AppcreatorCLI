<script setup lang="ts">
/** Hulpartikel: one help article, rendered from Markdown. */
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@lucide/vue'

import { allArticles, categoryTitle, visibleArticles } from '@/lib/help/articles'
import { renderArticle } from '@/lib/help/render'

const route = useRoute()
const router = useRouter()

const articles = visibleArticles(allArticles)
const article = computed(() => articles.find((a) => a.id === `${route.params.category}/${route.params.slug}`))

// Safe: markdown-it runs with `html: false`, so an article cannot inject HTML.
const html = computed(() => (article.value ? renderArticle(article.value.body, article.value.id) : ''))

/** Internal article links navigate via the router instead of reloading the page. */
function onClick(event: MouseEvent) {
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey) return
  const link = (event.target as HTMLElement | null)?.closest('a[data-internal]')
  const href = link?.getAttribute('href')
  if (!href) return
  event.preventDefault()
  void router.push(href)
}
</script>

<template>
  <div class="mx-auto flex max-w-2xl flex-col gap-6 py-2">
    <RouterLink
      :to="{ name: 'help' }"
      class="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-sm"
    >
      <ArrowLeft class="size-4" aria-hidden="true" />
      Terug naar Hulp
    </RouterLink>

    <article v-if="article" data-testid="help-article" class="flex flex-col gap-4">
      <header class="flex flex-col gap-1">
        <p class="text-primary text-xs font-semibold tracking-wide uppercase">{{ categoryTitle(article.category) }}</p>
        <h1 class="flex items-center gap-3 text-2xl font-bold">
          {{ article.title }}
          <span
            v-if="article.status === 'draft'"
            data-testid="draft-label"
            class="text-muted-foreground rounded-full border px-2 py-0.5 text-xs font-medium"
          >
            Concept
          </span>
        </h1>
      </header>
      <!-- eslint-disable-next-line vue/no-v-html -- rendered by markdown-it with html disabled -->
      <div class="help-body bg-card rounded-xl border p-5" @click="onClick" v-html="html" />
    </article>

    <section v-else data-testid="help-not-found" class="bg-card flex flex-col gap-2 rounded-xl border p-6">
      <h1 class="text-xl font-bold">Artikel niet gevonden</h1>
      <p class="text-muted-foreground">Dit hulpartikel bestaat niet (meer). Kijk in de hulp wat je nodig hebt.</p>
    </section>
  </div>
</template>

<style scoped>
.help-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  line-height: 1.7;
}
.help-body :deep(*) {
  margin: 0;
}
.help-body :deep(h2) {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--foreground);
}
.help-body :deep(p),
.help-body :deep(li) {
  color: var(--muted-foreground);
}
.help-body :deep(strong) {
  font-weight: 600;
  color: var(--foreground);
}
.help-body :deep(a) {
  color: var(--primary);
  text-decoration: underline;
  text-underline-offset: 4px;
}
.help-body :deep(ol) {
  list-style: decimal;
  padding-left: 1.5rem;
}
.help-body :deep(ul) {
  list-style: disc;
  padding-left: 1.5rem;
}
</style>
