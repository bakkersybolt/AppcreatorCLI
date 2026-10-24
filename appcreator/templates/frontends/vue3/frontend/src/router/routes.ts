import type { RouteRecordRaw } from 'vue-router'

/** All routes. Separate from `index.ts` so tests (`mountView` in `src/test/helpers.ts`) can reuse them. */
export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },
]
