import MarkdownIt from 'markdown-it'

/** HTML in markdown is disabled: articles are rendered with `v-html`, so raw HTML must never pass. */
const md = new MarkdownIt({ html: false, linkify: false, typographer: true })

/**
 * Resolve a relative `.md` link in article `fromId` (`<category>/<slug>`) to the router path
 * `/help/<category>/<slug>`. Returns null for external links, anchors and other links.
 */
export function resolveArticleLink(href: string, fromId: string): string | null {
  if (/^[a-z][a-z0-9+.-]*:/i.test(href) || href.startsWith('#') || href.startsWith('/')) return null
  const [path = '', hash] = href.split('#')
  if (!path.endsWith('.md')) return null
  const base = fromId.split('/').slice(0, -1).join('/')
  const target = new URL(path, `http://x/${base}/`).pathname.replace(/^\//, '').replace(/\.md$/, '')
  return `/help/${target}${hash ? `#${hash}` : ''}`
}

/** Render an article body to safe HTML; internal article links get a `/help/...` href and `data-internal`. */
export function renderArticle(body: string, fromId: string): string {
  const tokens = md.parse(body, {})
  for (const token of tokens) {
    for (const child of token.children ?? []) {
      if (child.type !== 'link_open') continue
      const href = String(child.attrGet('href') ?? '')
      const internal = resolveArticleLink(href, fromId)
      if (internal) {
        child.attrSet('href', internal)
        child.attrSet('data-internal', '')
      } else if (/^https?:/i.test(href)) {
        child.attrSet('target', '_blank')
        child.attrSet('rel', 'noopener noreferrer')
      }
    }
  }
  return md.renderer.render(tokens, md.options, {})
}
