// frontend/nuxt.config.ts
import tailwindcss from "@tailwindcss/vite"; // <-- 1. Nhớ import cái này

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  srcDir: 'app/',

  // 2. Khai báo đường dẫn đến file CSS (nơi có @import "tailwindcss")
  css: ['~/assets/css/main.css'],

  // 3. Kích hoạt plugin Tailwind v4
  vite: {
    plugins: [
      tailwindcss(),
    ],
  },
})