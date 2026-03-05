<script setup lang="ts">
import { Users, LogOut } from 'lucide-vue-next'

// 1. Lấy user và hàm logout từ composable
const { user, logout } = useAuth()
const route = useRoute()

// Không cần router hay handleLogout thủ công nữa vì useAuth đã xử lý
</script>

<template>
  <div class="shell-wrap">
    <header class="glass-header sticky top-0 z-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-gray-900 font-bold text-xl">Quản trị hệ thống</h1>
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
      <nav class="surface-card card-hover mb-6 flex gap-3 p-3">
        <NuxtLink
          to="/admin"
          :class="[
            'nav-pill flex items-center gap-2',
            route.path === '/admin' ? 'nav-pill-active' : 'nav-pill-idle'
          ]"
        >
          <Users class="w-5 h-5" />
          Quản lý tài khoản
        </NuxtLink>
      </nav>

      <slot />
    </div>
  </div>
</template>
