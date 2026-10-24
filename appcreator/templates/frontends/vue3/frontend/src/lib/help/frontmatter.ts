/**
 * Minimal frontmatter parser for the help articles in `src/content/help/`.
 *
 * Supports the subset the articles use: `key: value` and inline lists `key: [a, b]`.
 */

export const ARTICLE_STATUSES = ['draft', 'published'] as const

export type ArticleStatus = (typeof ARTICLE_STATUSES)[number]

export interface ArticleFrontmatter {
  title: string
  category: string
  keywords: string[]
  /** Optional: who the article is for (empty or absent = everyone). Not used for filtering yet. */
  roles: string[]
  status: ArticleStatus
  updated: string
}

export interface ParsedArticle {
  data: Record<string, string | string[]>
  body: string
}

const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/

export function parseFrontmatter(source: string): ParsedArticle {
  const match = FRONTMATTER_RE.exec(source)
  if (!match) return { data: {}, body: source }

  const data: Record<string, string | string[]> = {}
  for (const line of (match[1] ?? '').split(/\r?\n/)) {
    const sep = line.indexOf(':')
    if (sep === -1 || !line.trim()) continue
    const key = line.slice(0, sep).trim()
    const raw = line.slice(sep + 1).trim()
    if (raw.startsWith('[') && raw.endsWith(']')) {
      data[key] = raw
        .slice(1, -1)
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean)
    } else {
      data[key] = raw
    }
  }
  return { data, body: match[2] ?? '' }
}

/** Validate parsed frontmatter; returns a list of problems in Dutch (empty when valid). */
export function validateFrontmatter(
  data: Record<string, string | string[]>,
  categoryKeys: readonly string[],
): string[] {
  const errors: string[] = []
  const text = (key: string) => (typeof data[key] === 'string' ? (data[key] as string) : '')
  const list = (key: string) => (Array.isArray(data[key]) ? (data[key] as string[]) : null)

  if (!text('title')) errors.push('title ontbreekt')
  if (!categoryKeys.includes(text('category'))) errors.push(`onbekende category "${text('category')}"`)
  const keywords = list('keywords')
  if (!keywords || keywords.length === 0) errors.push('keywords is leeg')
  if ('roles' in data && !list('roles')) errors.push('roles moet een lijst zijn, bijv. [] voor iedereen')
  if (!(ARTICLE_STATUSES as readonly string[]).includes(text('status')))
    errors.push(`ongeldige status "${text('status')}"`)
  if (!text('updated')) errors.push('updated ontbreekt')
  return errors
}

/** Word count of the article body, excluding tables, code blocks and HTML comments. */
export function countWords(body: string): number {
  const prose = body
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .split(/\r?\n/)
    .filter((line) => !line.trim().startsWith('|'))
    .join(' ')
    .replace(/[#*_>`[\]()-]/g, ' ')
  return prose.split(/\s+/).filter((word) => /[\p{L}\p{N}]/u.test(word)).length
}
