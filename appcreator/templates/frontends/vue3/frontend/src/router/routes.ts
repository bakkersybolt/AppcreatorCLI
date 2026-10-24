import type { RouteRecordRaw } from 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    /** Help article of the screen, `<category>/<slug>` in `src/content/help/`; the **?** button opens it. */
    help?: string
    /** Development-only screen (design sandbox); not registered in a production build. */
    devOnly?: boolean
  }
}

/**
 * Development-only screens: the design sandbox (`src/design/`, skill `design-system`). Registered only in
 * `npm run dev` (and tests); the documentation checks skip them.
 */
const devRoutes: RouteRecordRaw[] = import.meta.env.DEV
  ? [
      {
        path: '/_ontwerp',
        name: 'design',
        component: () => import('@/design/DesignIndex.vue'),
        meta: { devOnly: true },
      },
      {
        path: '/_ontwerp/:scherm',
        name: 'design-screen',
        component: () => import('@/design/DesignScreen.vue'),
        meta: { devOnly: true },
      },
    ]
  : []

/**
 * All routes. Separate from `index.ts` so tests (`mountView` in `src/test/helpers.ts`) can reuse them.
 * Each route except the 404 and the development-only screens has `meta.help` pointing to a help article;
 * `src/content/help/__tests__/docs.spec.ts` enforces this.
 */
export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { help: 'aan-de-slag/welkom' },
  },
  {
    path: '/help',
    name: 'help',
    component: () => import('@/views/help/HelpView.vue'),
    meta: { help: 'aan-de-slag/welkom' },
  },
  {
    path: '/help/:category/:slug',
    name: 'help-article',
    component: () => import('@/views/help/HelpArticleView.vue'),
    meta: { help: 'aan-de-slag/welkom' },
  },
  ...devRoutes,
]
