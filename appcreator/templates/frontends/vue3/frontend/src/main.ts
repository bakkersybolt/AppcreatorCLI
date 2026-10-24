import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './lib/zod-nl' // Dutch default texts for zod rules without their own message
import './assets/index.css' // Tailwind, the shadcn theme and the brand tokens

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
