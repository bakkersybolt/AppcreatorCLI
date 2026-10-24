import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.{spec,test}.ts'],
    setupFiles: ['src/test/setup.ts'],
    restoreMocks: true,
    // Node 25+ ships its own (empty) global localStorage that shadows jsdom's; switch it off.
    poolOptions: { forks: { execArgv: ['--no-experimental-webstorage'] } },
  },
})
