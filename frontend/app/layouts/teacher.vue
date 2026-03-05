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
  <div class="shell-wrap">
    <header class="glass-header sticky top-0 z-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-gray-900 font-bold text-xl">Trang Giảng viên</h1>
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
          to="/teacher"
          :class="[
            'nav-pill flex items-center gap-2',
            isActive('/teacher') && !route.path.includes('questions') && !route.path.includes('exams') && !route.path.includes('statistics')
              ? 'nav-pill-active'
              : 'nav-pill-idle'
          ]"
        >
          <Users class="w-5 h-5" />
          Quản lý Lớp học
        </NuxtLink>

        <NuxtLink
          to="/teacher/questions"
          :class="['nav-pill flex items-center gap-2', isActive('/teacher/questions') ? 'nav-pill-active' : 'nav-pill-idle']"
        >
          <BookOpen class="w-5 h-5" />
          Ngân hàng câu hỏi
        </NuxtLink>

        <NuxtLink
          to="/teacher/exams"
          :class="['nav-pill flex items-center gap-2', isActive('/teacher/exams') ? 'nav-pill-active' : 'nav-pill-idle']"
        >
          <FileText class="w-5 h-5" />
          Quản lý Đề thi
        </NuxtLink>

        <NuxtLink
          to="/teacher/statistics"
          :class="['nav-pill flex items-center gap-2', isActive('/teacher/statistics') ? 'nav-pill-active' : 'nav-pill-idle']"
        >
          <BarChart3 class="w-5 h-5" />
          Thống kê & Báo cáo
        </NuxtLink>
      </nav>

      <slot />
    </div>
  </div>
</template>
