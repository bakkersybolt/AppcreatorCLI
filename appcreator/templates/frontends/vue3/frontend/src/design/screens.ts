import type { Component } from 'vue'

/**
 * The screens of the design sandbox (`/_ontwerp`, only in `npm run dev`). A sandbox screen is a design built
 * with the real components and fixed data, without API or store; the skill `design-system` builds a design
 * here first and only then in the real view.
 */
export interface DesignScreen {
  /** Part of the URL: `/_ontwerp/<key>`. */
  key: string
  title: string
  description: string
  component: () => Promise<{ default: Component }>
}

export const designScreens: DesignScreen[] = [
  {
    key: 'voorbeeld',
    title: 'Voorbeeldscherm',
    description: 'Kleuren, letters, knoppen, een formulier en meldingen in de huidige uitstraling.',
    component: () => import('./screens/VoorbeeldScherm.vue'),
  },
]
