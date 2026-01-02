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
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-gray-900 font-bold text-xl">Trang Sinh viên</h1>
            <p class="text-gray-600">Xin chào, {{ user?.fullName }}</p>
          </div>
          <button
            @click="logout"
            class="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <LogOut class="w-5 h-5" />
            Đăng xuất
          </button>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <nav class="mb-6 flex flex-wrap gap-4">
        <NuxtLink
          to="/student"
          :class="[
            'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
            isActive('/student') && !route.path.includes('history') && !route.path.includes('exam')
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100'
          ]"
        >
          <FileText class="w-5 h-5" />
          Bài thi của tôi
        </NuxtLink>

        <NuxtLink
          to="/student/history"
          :class="['flex items-center gap-2 px-4 py-2 rounded-lg transition-colors', isActive('/student/history') ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100']"
        >
          <History class="w-5 h-5" />
          Lịch sử thi
        </NuxtLink>
      </nav>

      <slot />
    </div>
  </div>
</template>