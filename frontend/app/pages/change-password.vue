<script setup lang="ts">
definePageMeta({})

const config = useRuntimeConfig()
const tokenCookie = useCookie<string | null>('token')
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const message = ref('')
const error = ref('')

const submit = async () => {
  message.value = ''
  error.value = ''
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Mật khẩu xác nhận không khớp'
    return
  }
  loading.value = true
  try {
    await $fetch('/change-password', {
      method: 'POST',
      baseURL: config.public.apiBase,
      headers: { Authorization: `Bearer ${tokenCookie.value || ''}` },
      body: {
        current_password: currentPassword.value,
        new_password: newPassword.value
      }
    })
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    message.value = 'Đổi mật khẩu thành công'
  } catch (err: any) {
    error.value = err?.data?.detail || 'Không thể đổi mật khẩu'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="mx-auto max-w-lg p-6">
    <form class="surface-card space-y-4 p-6" @submit.prevent="submit">
      <h1 class="text-2xl font-bold">Đổi mật khẩu</h1>
      <p v-if="message" class="rounded-lg bg-green-50 p-3 text-green-700">{{ message }}</p>
      <p v-if="error" class="rounded-lg bg-red-50 p-3 text-red-700">{{ error }}</p>
      <input v-model="currentPassword" type="password" required class="input-field" placeholder="Mật khẩu hiện tại" />
      <input v-model="newPassword" type="password" minlength="8" maxlength="72" required class="input-field" placeholder="Mật khẩu mới" />
      <input v-model="confirmPassword" type="password" minlength="8" maxlength="72" required class="input-field" placeholder="Xác nhận mật khẩu mới" />
      <button :disabled="loading" class="btn-primary w-full disabled:opacity-60">
        {{ loading ? 'Đang xử lý...' : 'Đổi mật khẩu' }}
      </button>
    </form>
  </main>
</template>
