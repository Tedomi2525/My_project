<script setup lang="ts">
import { Users, BookOpen, FileText, BarChart3, LogOut } from 'lucide-vue-next'

// ✅ CHỈ GỌI useAuth 1 LẦN
const auth = useAuth()
const { user, logout, fetchUser } = auth

const route = useRoute()

// ✅ đảm bảo user được restore TRƯỚC KHI render
await fetchUser()

// active link
const isActive = (path: string) => {
  if (path === '/teacher' && route.path === '/teacher') return true
  if (path !== '/teacher' && route.path.startsWith(path)) return true
  return false
}
</script>


<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-gray-900 font-bold text-xl">Trang Giảng viên</h1>
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
          to="/teacher"
          :class="[
            'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
            isActive('/teacher') && !route.path.includes('questions') && !route.path.includes('exams') && !route.path.includes('statistics')
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100'
          ]"
        >
          <Users class="w-5 h-5" />
          Quản lý Lớp học
        </NuxtLink>

        <NuxtLink
          to="/teacher/questions"
          :class="['flex items-center gap-2 px-4 py-2 rounded-lg transition-colors', isActive('/teacher/questions') ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100']"
        >
          <BookOpen class="w-5 h-5" />
          Ngân hàng câu hỏi
        </NuxtLink>

        <NuxtLink
          to="/teacher/exams"
          :class="['flex items-center gap-2 px-4 py-2 rounded-lg transition-colors', isActive('/teacher/exams') ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100']"
        >
          <FileText class="w-5 h-5" />
          Quản lý Đề thi
        </NuxtLink>

        <NuxtLink
          to="/teacher/statistics"
          :class="['flex items-center gap-2 px-4 py-2 rounded-lg transition-colors', isActive('/teacher/statistics') ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100']"
        >
          <BarChart3 class="w-5 h-5" />
          Thống kê & Báo cáo
        </NuxtLink>
      </nav>

      <slot />
    </div>
  </div>
</template>