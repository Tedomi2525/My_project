<script setup lang="ts">
import { GraduationCap, LogOut, UserCheck, Users, ScrollText, KeyRound } from 'lucide-vue-next'

const { user, logout } = useAuth()
const route = useRoute()
</script>

<template>
  <div class="shell-wrap">
    <header class="glass-header sticky top-0 z-20">
      <div class="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-bold text-gray-900">Quản trị hệ thống</h1>
            <p class="text-gray-600">Xin chào, {{ user?.fullName }}</p>
          </div>
          <NuxtLink to="/change-password" class="btn-secondary">Đổi mật khẩu</NuxtLink>
          <button
            @click="logout"
            class="btn-ghost-danger"
          >
            <LogOut class="h-5 w-5" />
            Đăng xuất
          </button>
        </div>
      </div>
    </header>

    <div class="soft-enter-delay mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <nav class="surface-card card-hover mb-6 flex flex-wrap gap-3 p-3">
        <NuxtLink
          to="/admin"
          :class="[
            'nav-pill flex items-center gap-2',
            route.path === '/admin' ? 'nav-pill-active' : 'nav-pill-idle'
          ]"
        >
          <UserCheck class="h-5 w-5" />
          Yêu cầu tài khoản
        </NuxtLink>
        <NuxtLink
          to="/admin/teachers"
          :class="[
            'nav-pill flex items-center gap-2',
            route.path === '/admin/teachers' ? 'nav-pill-active' : 'nav-pill-idle'
          ]"
        >
          <GraduationCap class="h-5 w-5" />
          Quản lý giáo viên
        </NuxtLink>
        <NuxtLink
          to="/admin/students"
          :class="[
            'nav-pill flex items-center gap-2',
            route.path === '/admin/students' ? 'nav-pill-active' : 'nav-pill-idle'
          ]"
        >
          <Users class="h-5 w-5" />
          Quản lý sinh viên
        </NuxtLink>
        <NuxtLink
          to="/admin/audit"
          :class="['nav-pill flex items-center gap-2', route.path === '/admin/audit' ? 'nav-pill-active' : 'nav-pill-idle']"
        >
          <ScrollText class="h-5 w-5" />
          Nhật ký hệ thống
        </NuxtLink>
      </nav>

      <slot />
    </div>
  </div>
</template>
