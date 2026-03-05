<script setup lang="ts">
import { FileText, History, LogOut } from 'lucide-vue-next'

// 1. Lấy user và logout từ composable
const { user, logout } = useAuth()
const route = useRoute()

// Hàm kiểm tra active link
const isActive = (path: string) => {
  if (path === '/student' && route.path === '/student') return true
  if (path !== '/student' && route.path.startsWith(path)) return true
  return false
}
</script>

<template>
  <div class="shell-wrap">
    <header class="glass-header sticky top-0 z-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-gray-900 font-bold text-xl">Trang Sinh viên</h1>
            <p class="text-gray-600">Xin chào, {{ user?.fullName }}</p>
          </div>
          <button
            @click="logout"
            class="btn-ghost-danger"
          >
            <LogOut class="w-5 h-5" />
            Đăng xuất
          </button>
        </div>
      </div>
    </header>

    <div class="soft-enter-delay max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <nav class="surface-card card-hover mb-6 flex flex-wrap gap-3 p-3">
        <NuxtLink
          to="/student"
          :class="[
            'nav-pill flex items-center gap-2',
            isActive('/student') && !route.path.includes('history') && !route.path.includes('exam')
              ? 'nav-pill-active'
              : 'nav-pill-idle'
          ]"
        >
          <FileText class="w-5 h-5" />
          Bài thi của tôi
        </NuxtLink>

        <NuxtLink
          to="/student/history"
          :class="['nav-pill flex items-center gap-2', isActive('/student/history') ? 'nav-pill-active' : 'nav-pill-idle']"
        >
          <History class="w-5 h-5" />
          Lịch sử thi
        </NuxtLink>
      </nav>

      <slot />
    </div>
  </div>
</template>
