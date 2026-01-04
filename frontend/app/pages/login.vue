<script setup lang="ts">
import { LogIn } from 'lucide-vue-next'

// ❌ Không dùng layout
definePageMeta({
  layout: false
})

// 👉 Lấy login + user từ useAuth
const { login, user } = useAuth()

// ===== STATE =====
const username = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const showForgotPassword = ref(false)
const email = ref('')
const resetMessage = ref('')

// ===== ACTIONS =====
const handleSubmit = async () => {
  error.value = ''
  isLoading.value = true

  // Gọi login (login chỉ set user + token)
  await login(username.value, password.value)

  // ❌ Login thất bại
  if (!user.value) {
    error.value = 'Tên đăng nhập hoặc mật khẩu không đúng'
    isLoading.value = false
    return
  }

  // ✅ Login thành công → điều hướng theo role
  switch (user.value.role) {
    case 'admin':
      await navigateTo('/admin')
      break
    case 'teacher':
      await navigateTo('/teacher')
      break
    case 'student':
      await navigateTo('/student')
      break
    default:
      error.value = 'Không xác định được quyền người dùng'
      isLoading.value = false
  }
}

const handleForgotPassword = () => {
  resetMessage.value = 'Đã gửi email hướng dẫn đặt lại mật khẩu đến ' + email.value
  setTimeout(() => {
    showForgotPassword.value = false
    resetMessage.value = ''
    email.value = ''
  }, 3000)
}
</script>

<template>
  <div v-if="showForgotPassword" class="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
      <h2 class="text-center mb-6 font-bold text-2xl">Quên mật khẩu</h2>
      
      <div v-if="resetMessage" class="bg-green-50 text-green-700 p-4 rounded-lg mb-4">
        {{ resetMessage }}
      </div>
      
      <form v-else @submit.prevent="handleForgotPassword">
        <div class="mb-4">
          <label for="email" class="block mb-2 font-medium">Email</label>
          <input
            type="email"
            id="email"
            v-model="email"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        <button
          type="submit"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors mb-4 font-bold"
        >
          Gửi email khôi phục
        </button>
        <button
          type="button"
          @click="showForgotPassword = false"
          class="w-full text-gray-600 hover:text-gray-800"
        >
          Quay lại đăng nhập
        </button>
      </form>
    </div>
  </div>

  <div v-else class="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
    <div class="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
      <div class="flex items-center justify-center mb-6">
        <div class="bg-blue-600 p-3 rounded-full">
          <LogIn class="w-8 h-8 text-white" />
        </div>
      </div>
      <h1 class="text-center mb-2 font-bold text-2xl">Hệ thống Thi trắc nghiệm</h1>
      <p class="text-center text-gray-600 mb-6">Đăng nhập để tiếp tục</p>

      <div v-if="error" class="bg-red-50 text-red-600 p-3 rounded-lg mb-4 flex gap-2 items-center">
        <span>⚠️</span> {{ error }}
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="mb-4">
          <label for="username" class="block mb-2 font-medium">Tên đăng nhập</label>
          <input
            type="text"
            id="username"
            v-model="username"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
            :disabled="isLoading" 
          />
        </div>

        <div class="mb-6">
          <label for="password" class="block mb-2 font-medium">Mật khẩu</label>
          <input
            type="password"
            id="password"
            v-model="password"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
            :disabled="isLoading"
          />
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors mb-4 font-bold disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center"
        >
          <span v-if="isLoading" class="mr-2 animate-spin">⚪</span>
          {{ isLoading ? 'Đang xử lý...' : 'Đăng nhập' }}
        </button>

        <button
          type="button"
          @click="showForgotPassword = true"
          class="w-full text-blue-600 hover:text-blue-800 text-sm"
          :disabled="isLoading"
        >
          Quên mật khẩu?
        </button>
      </form>

      <div class="mt-8 p-4 bg-gray-50 rounded-lg">
        <p class="text-sm text-gray-600 mb-2 font-semibold">Tài khoản demo:</p>
        <div class="space-y-1 font-mono text-xs text-gray-500">
          <p>Admin: admin / admin123</p>
          <p>Giảng viên: teacher / teacher123</p>
          <p>Sinh viên: student / student123</p>
        </div>
      </div>
    </div>
  </div>
</template>