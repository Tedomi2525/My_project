<script setup lang="ts">
definePageMeta({ layout: false })

const config = useRuntimeConfig()
const route = useRoute()
const token = ref(String(route.query.token || ''))
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const message = ref('')
const error = ref('')

const submit = async () => {
  error.value = ''
  message.value = ''
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Mật khẩu xác nhận không khớp'
    return
  }
  loading.value = true
  try {
    await $fetch('/reset-password', {
      method: 'POST',
      baseURL: config.public.apiBase,
      body: { token: token.value, new_password: newPassword.value }
    })
    message.value = 'Đặt lại mật khẩu thành công. Bạn có thể đăng nhập ngay.'
  } catch (err: any) {
    error.value = err?.data?.detail || 'Không thể đặt lại mật khẩu'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="flex min-h-screen items-center justify-center bg-slate-50 p-4">
    <form class="surface-card w-full max-w-md space-y-4 p-8" @submit.prevent="submit">
      <h1 class="text-2xl font-bold">Đặt lại mật khẩu</h1>
      <p v-if="message" class="rounded-lg bg-green-50 p-3 text-green-700">{{ message }}</p>
      <p v-if="error" class="rounded-lg bg-red-50 p-3 text-red-700">{{ error }}</p>
      <label class="block">
        <span class="mb-1 block font-medium">Mã đặt lại mật khẩu</span>
        <input v-model="token" required class="input-field" />
      </label>
      <label class="block">
        <span class="mb-1 block font-medium">Mật khẩu mới</span>
        <input v-model="newPassword" type="password" minlength="8" maxlength="72" required class="input-field" />
      </label>
      <label class="block">
        <span class="mb-1 block font-medium">Xác nhận mật khẩu</span>
        <input v-model="confirmPassword" type="password" minlength="8" maxlength="72" required class="input-field" />
      </label>
      <button :disabled="loading" class="btn-primary w-full disabled:opacity-60">
        {{ loading ? 'Đang xử lý...' : 'Đặt lại mật khẩu' }}
      </button>
      <NuxtLink to="/login" class="block text-center text-blue-600">Quay lại đăng nhập</NuxtLink>
    </form>
  </main>
</template>
