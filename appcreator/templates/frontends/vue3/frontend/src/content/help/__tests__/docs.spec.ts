/**
 * Documentation checks (skill `documentatie`): every route except the 404 and the development-only screens
 * (path starting with `/_` or `meta.devOnly`) has `meta.help` pointing to an existing article; frontmatter is
 * valid; articles stay under 250 words; internal links work.
 * Do not loosen these checks to close a sprint.
 */
import { describe, expect, it } from 'vitest'
import type { RouteRecordRaw } from 'vue-router'

import { routes } from '@/router/routes'
import { countWords, parseFrontmatter, validateFrontmatter } from '@/lib/help/frontmatter'
import categoriesJson from '../categories.json'

const MAX_WORDS = 250

const sources = import.meta.glob('../**/*.md', { query: '?raw', import: 'default', eager: true }) as Record<
  string,
  string
>

/** `../aan-de-slag/welkom.md` → `aan-de-slag/welkom` */
const articles = new Map(
  Object.entries(sources).map(([path, source]) => [path.replace(/^\.\.\//, '').replace(/\.md$/, ''), source]),
)
const categoryKeys = categoriesJson.categories.map((category) => category.key)

/** Routes a user can reach: not the 404 and not the development-only screens (`/_ontwerp`, ...). */
function needsHelp(route: RouteRecordRaw): boolean {
  return route.name !== 'not-found' && !route.path.startsWith('/_') && !route.meta?.devOnly
}

describe('help routes', () => {
  const helpRoutes = routes.filter(needsHelp)

  it('there is at least one route to check', () => {
    expect(helpRoutes.length).toBeGreaterThan(0)
  })

  it.each(helpRoutes.map((route) => [route.path, route.meta?.help] as const))(
    'route %s has meta.help pointing to an existing article',
    (_path, help) => {
      expect(help, 'meta.help ontbreekt').toBeTypeOf('string')
      expect(articles.has(help as string), `artikel ${help}.md bestaat niet`).toBe(true)
    },
  )
})

describe('help articles', () => {
  it('there is at least one article', () => {
    expect(articles.size).toBeGreaterThan(0)
  })

  it('categories.json has unique keys', () => {
    expect(new Set(categoryKeys).size).toBe(categoryKeys.length)
  })

  for (const [key, source] of articles) {
    describe(key, () => {
      const { data, body } = parseFrontmatter(source)

      it('has valid frontmatter', () => {
        expect(validateFrontmatter(data, categoryKeys)).toEqual([])
      })

      it('lives in the folder of its category', () => {
        expect(key.split('/')[0]).toBe(data.category)
      })

      it(`has at most ${MAX_WORDS} words`, () => {
        expect(countWords(body)).toBeLessThanOrEqual(MAX_WORDS)
      })

      it('has working internal links', () => {
        const links = [...body.matchAll(/\]\(([^)\s]+)\)/g)].map((m) => m[1] ?? '')
        const internal = links.filter((link) => !/^[a-z]+:/i.test(link) && !link.startsWith('#'))
        for (const link of internal) {
          const base = key.split('/').slice(0, -1)
          const target = new URL(link.replace(/#.*$/, ''), `http://x/${base.join('/')}/`).pathname
            .replace(/^\//, '')
            .replace(/\.md$/, '')
          expect(articles.has(target), `link ${link} wijst naar een onbekend artikel`).toBe(true)
        }
      })
    })
  }
})
