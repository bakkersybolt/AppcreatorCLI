/**
 * Help articles from `src/content/help/`: loading, validation, visibility and a simple filter.
 *
 * `status: draft` articles are shown only in development (`import.meta.env.DEV`), marked "Concept";
 * production builds hide them.
 */
import categoriesJson from '@/content/help/categories.json'
import { parseFrontmatter, validateFrontmatter, type ArticleFrontmatter, type ArticleStatus } from './frontmatter'

export interface HelpCategory {
  key: string
  title: string
}

export interface HelpArticle extends ArticleFrontmatter {
  /** `<category>/<slug>`, matches route `meta.help`. */
  id: string
  slug: string
  body: string
}

export const categories: HelpCategory[] = categoriesJson.categories

const sources = import.meta.glob('../../content/help/**/*.md', {
  query: '?raw',
  import: 'default',
  eager: true,
}) as Record<string, string>

/** `../../content/help/aan-de-slag/welkom.md` → `aan-de-slag/welkom` */
export function pathToId(path: string): string {
  return path.replace(/^.*content\/help\//, '').replace(/\.md$/, '')
}

/** Parse and validate raw sources; invalid articles are skipped (the docs checks fail on them). */
export function loadArticles(raw: Record<string, string>, categoryKeys: readonly string[]): HelpArticle[] {
  const result: HelpArticle[] = []
  for (const [path, source] of Object.entries(raw)) {
    const { data, body } = parseFrontmatter(source)
    if (validateFrontmatter(data, categoryKeys).length > 0) continue
    const id = pathToId(path)
    result.push({
      id,
      slug: id.split('/').slice(1).join('/'),
      body,
      title: data.title as string,
      category: data.category as string,
      keywords: data.keywords as string[],
      roles: (data.roles as string[] | undefined) ?? [],
      status: data.status as ArticleStatus,
      updated: data.updated as string,
    })
  }
  return result.sort((a, b) => a.title.localeCompare(b.title, 'nl'))
}

/** The articles a reader may see: drafts only when `includeDrafts` (development). */
export function visibleArticles(list: HelpArticle[], includeDrafts: boolean = import.meta.env.DEV): HelpArticle[] {
  return list.filter((article) => article.status !== 'draft' || includeDrafts)
}

/** Articles whose title or keywords contain every word of `query` (case-insensitive); all for an empty query. */
export function filterArticles(list: HelpArticle[], query: string): HelpArticle[] {
  const words = query.toLocaleLowerCase('nl').split(/\s+/).filter(Boolean)
  if (words.length === 0) return list
  return list.filter((article) => {
    const haystack = [article.title, ...article.keywords].join(' ').toLocaleLowerCase('nl')
    return words.every((word) => haystack.includes(word))
  })
}

/** Categories that have at least one article, in `categories.json` order. */
export function groupByCategory(list: HelpArticle[], cats: HelpCategory[] = categories) {
  return cats
    .map((category) => ({ category, articles: list.filter((a) => a.category === category.key) }))
    .filter((group) => group.articles.length > 0)
}

export function categoryTitle(key: string, cats: HelpCategory[] = categories): string {
  return cats.find((c) => c.key === key)?.title ?? 'Hulp'
}

export const allArticles: HelpArticle[] = loadArticles(
  sources,
  categories.map((c) => c.key),
)
