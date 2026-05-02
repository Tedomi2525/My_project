// plugins/api.ts
import axios from 'axios'
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const api = axios.create({
    baseURL: config.public.apiBase
  })

  return {
    provide: { api }
  }
})
