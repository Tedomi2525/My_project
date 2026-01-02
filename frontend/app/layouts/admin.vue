<script setup lang="ts">
import { Users, LogOut } from 'lucide-vue-next'

// 1. Lấy user và hàm logout từ composable
const { user, logout } = useAuth()
const route = useRoute()

// Không cần router hay handleLogout thủ công nữa vì useAuth đã xử lý
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-gray-900 font-bold text-xl">Quản trị hệ thống</h1>
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
      <nav class="mb-6 flex gap-4">
        <NuxtLink
          to="/admin"
          :class="[
            'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
            route.path === '/admin' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
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