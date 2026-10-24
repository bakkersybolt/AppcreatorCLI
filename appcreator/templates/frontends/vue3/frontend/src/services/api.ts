import axios from 'axios'

export const api = axios.create({
  // Relative: in development the Vite proxy forwards /api to the backend (see vite.config.ts).
  // Set VITE_API_URL only when the API lives on another origin.
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Optioneel: JWT interceptor toevoegen
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Centrale foutafhandeling
    return Promise.reject(error)
  }
)

export default api
