<script setup lang="ts">
/** Hulp: the help articles per category, with a filter on title and keywords. */
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { allArticles, filterArticles, groupByCategory, visibleArticles, type HelpArticle } from '@/lib/help/articles'

const articles = visibleArticles(allArticles)
const query = ref('')

const filtered = computed(() => filterArticles(articles, query.value))
const groups = computed(() => groupByCategory(filtered.value))

function articleRoute(article: HelpArticle) {
  return { name: 'help-article', params: { category: article.category, slug: article.slug } }
}
</script>

<template>
  <div class="mx-auto flex max-w-3xl flex-col gap-6 py-2">
    <h1 class="text-2xl font-bold">Hulp</h1>

    <p v-if="articles.length === 0" data-testid="no-articles" class="text-muted-foreground">
      Er zijn nog geen hulpartikelen.
    </p>

    <template v-else>
      <div class="flex flex-col gap-2">
        <Label for="help-filter">Zoek in de hulp</Label>
        <Input id="help-filter" v-model="query" type="search" placeholder="Bijvoorbeeld: starten" />
      </div>

      <p v-if="groups.length === 0" data-testid="no-results" class="text-muted-foreground">
        Niets gevonden voor “{{ query.trim() }}”. Probeer een ander woord.
      </p>

      <section
        v-for="group in groups"
        :key="group.category.key"
        :data-testid="`category-${group.category.key}`"
        class="bg-card flex flex-col gap-2 rounded-xl border p-4"
      >
        <h2 class="text-lg font-semibold">{{ group.category.title }}</h2>
        <ul class="flex flex-col">
          <li v-for="article in group.articles" :key="article.id">
            <RouterLink
              :to="articleRoute(article)"
              class="hover:bg-muted flex items-center justify-between gap-2 rounded-lg px-2 py-2"
            >
              <span>{{ article.title }}</span>
              <span
                v-if="article.status === 'draft'"
                class="text-muted-foreground rounded-full border px-2 py-0.5 text-xs font-medium"
              >
                Concept
              </span>
            </RouterLink>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>
