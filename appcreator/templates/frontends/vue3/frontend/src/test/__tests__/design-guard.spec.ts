/**
 * Design guard (rule `design-rules.md`, skill `design-system`): applies the rules of `frontend/design-guard.json`
 * to every file under `src/`, with the same semantics as the lint hook of the AI assistant, if any (Python `fnmatch` on paths
 * relative to `frontend/`, where `*` also matches `/`). Change the rules in that JSON file, not here.
 */
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative, sep } from 'node:path'
import { describe, expect, it } from 'vitest'

interface GuardRule {
  pattern: string
  message: string
  files?: string[]
  allow?: string[]
}

/** Vitest runs from `frontend/` (where `vitest.config.ts` is). */
const FRONTEND = process.cwd()
const guard = JSON.parse(readFileSync(join(FRONTEND, 'design-guard.json'), 'utf8')) as { rules: GuardRule[] }

/** Python `fnmatch.translate`: `*` → any characters (also `/`), `?` → one character, `[...]`/`[!...]` → a class. */
function globToRegExp(glob: string): RegExp {
  let source = ''
  for (let i = 0; i < glob.length; i++) {
    const char = glob[i]!
    if (char === '*') source += '.*'
    else if (char === '?') source += '.'
    else if (char === '[') {
      const end = glob.indexOf(']', i + 2)
      if (end === -1) source += '\\['
      else {
        let body = glob.slice(i + 1, end).replace(/\\/g, '\\\\')
        if (body.startsWith('!')) body = '^' + body.slice(1)
        else if (body.startsWith('^')) body = '\\' + body
        source += `[${body}]`
        i = end
      }
    } else source += char.replace(/[.+^${}()|\\\]]/g, '\\$&')
  }
  return new RegExp(`^${source}$`, 's')
}

function matchesAny(path: string, globs: string[]): boolean {
  return globs.some((glob) => globToRegExp(glob).test(path))
}

/** All files under `src/`, as paths relative to `frontend/` with forward slashes. */
function filesUnder(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name)
    if (statSync(path).isDirectory()) return filesUnder(path)
    return [relative(FRONTEND, path).split(sep).join('/')]
  })
}

/** The violations of `rules` in one file: `path:line: message`. */
function violations(rel: string, text: string, rules: GuardRule[] = guard.rules): string[] {
  const hits: string[] = []
  for (const rule of rules) {
    if (!matchesAny(rel, rule.files ?? ['src/**'])) continue
    if (matchesAny(rel, rule.allow ?? [])) continue
    const pattern = new RegExp(rule.pattern)
    text.split(/\r?\n/).forEach((line, index) => {
      if (pattern.test(line)) hits.push(`${rel}:${index + 1}: ${rule.message}\n    ${line.trim()}`)
    })
  }
  return hits
}

describe('design guard', () => {
  it('has rules', () => {
    expect(guard.rules.length).toBeGreaterThan(0)
  })

  it('src/ follows design-guard.json', () => {
    const files = filesUnder(join(FRONTEND, 'src'))
    expect(files.length).toBeGreaterThan(10)
    const hits = files.flatMap((rel) => violations(rel, readFileSync(join(FRONTEND, rel), 'utf8')))
    expect(hits).toEqual([])
  })

  it('matches globs like Python fnmatch', () => {
    expect(globToRegExp('src/*.vue').test('src/views/help/HelpView.vue')).toBe(true)
    expect(globToRegExp('src/*.vue').test('src/App.vue')).toBe(true)
    expect(globToRegExp('src/**').test('src/a/b.ts')).toBe(true)
    expect(globToRegExp('*/__tests__/*').test('src/views/__tests__/X.spec.ts')).toBe(true)
    expect(globToRegExp('src/?.ts').test('src/a.ts')).toBe(true)
    expect(globToRegExp('src/[!x].ts').test('src/x.ts')).toBe(false)
    expect(globToRegExp('src/*.vue').test('src/a.vue.bak')).toBe(false)
  })

  it('flags colours and dark variants in views, not elsewhere', () => {
    const view = 'src/views/SomeView.vue'
    const flagged = (line: string, rel = view) => violations(rel, line).length > 0
    expect(flagged('<div class="bg-[#ff0000] p-2">')).toBe(true)
    expect(flagged('<div class="text-[oklch(0.5_0.2_30)]">')).toBe(true)
    expect(flagged('<div class="bg-card dark:bg-black">')).toBe(true)
    expect(flagged('  color: #fff;')).toBe(true)
    expect(flagged(`const style = { color: '#a1b2c3' }`)).toBe(true)
    expect(flagged('<div class="bg-primary text-primary-foreground">')).toBe(false)
    expect(flagged('<template #default="{ item }">')).toBe(false)
    expect(flagged('<template #add>')).toBe(false)
    expect(flagged('<a href="#inhoud">Naar de inhoud</a>')).toBe(false)
    expect(flagged('Tailwind would apply the `dark:` classes')).toBe(false)
    expect(flagged('<div class="rounded-[min(var(--radius-md),10px)]">')).toBe(false)
    expect(flagged('<div class="dark:bg-input/30">', 'src/components/ui/input/Input.vue')).toBe(false)
    expect(flagged('--brand-primary: #123456;', 'src/assets/brand/tokens.css')).toBe(false)
  })
})
