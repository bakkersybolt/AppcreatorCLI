// Global test setup (Vitest + jsdom), see `setupFiles` in vitest.config.ts.
import '@/lib/zod-nl'

// jsdom does not implement scrolling; vue-router's scrollBehavior calls it on every navigation.
window.scrollTo = () => {}
