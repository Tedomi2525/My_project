<script setup lang="ts">
import { LogIn, UserPlus } from 'lucide-vue-next'

// ❌ Không dùng layout
definePageMeta({
  layout: false
})

onMounted(() => {
  const { user, role } = useAuth()
  if (user.value) {
    switch (role.value) {
      case 'admin': return navigateTo('/admin')
      case 'teacher': return navigateTo('/teacher')
      case 'student': return navigateTo('/student')
    }
  }
})


// 👉 Lấy login + user từ useAuth
const { login, user } = useAuth()
const { createAccountRequest, getAccountRequestStatus } = useAccountRequests()

// ===== STATE =====
const username = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const showForgotPassword = ref(false)
const email = ref('')
const resetMessage = ref('')
const showAccountRequest = ref(false)
const isRequestLoading = ref(false)
const accountRequestMessage = ref('')
const accountRequestError = ref('')
const submittedRequestId = ref<number | null>(null)
const accountCredentials = ref<{ username: string; password: string } | null>(null)
let requestPollTimer: ReturnType<typeof setInterval> | null = null
const accountRequestForm = reactive({
  fullName: '',
  role: 'student' as 'student' | 'teacher',
  note: ''
})

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

const resetAccountRequestForm = () => {
  accountRequestForm.fullName = ''
  accountRequestForm.role = 'student'
  accountRequestForm.note = ''
}

const stopAccountRequestPolling = () => {
  if (requestPollTimer) {
    clearInterval(requestPollTimer)
    requestPollTimer = null
  }
}

const pollAccountRequestStatus = async () => {
  if (!submittedRequestId.value) return

  try {
    const status = await getAccountRequestStatus(submittedRequestId.value)
    accountRequestMessage.value = status.message

    if (status.status === 'approved' && status.username && status.password) {
      accountCredentials.value = {
        username: status.username,
        password: status.password
      }
      stopAccountRequestPolling()
    }

    if (status.status === 'rejected') {
      accountRequestError.value = status.message
      stopAccountRequestPolling()
    }
  } catch (err: any) {
    accountRequestError.value = err?.data?.detail || 'Không kiểm tra được trạng thái yêu cầu'
    stopAccountRequestPolling()
  }
}

const startAccountRequestPolling = () => {
  stopAccountRequestPolling()
  requestPollTimer = setInterval(pollAccountRequestStatus, 5000)
}

onUnmounted(() => stopAccountRequestPolling())

const handleAccountRequest = async () => {
  accountRequestError.value = ''
  accountRequestMessage.value = ''
  accountCredentials.value = null
  submittedRequestId.value = null
  stopAccountRequestPolling()
  isRequestLoading.value = true

  try {
    const request = await createAccountRequest({
      full_name: accountRequestForm.fullName,
      role: accountRequestForm.role,
      note: accountRequestForm.note || undefined
    })
    submittedRequestId.value = request.id
    accountRequestMessage.value = 'Yêu cầu đã được gửi. Vui lòng giữ trang này, hệ thống sẽ tự báo khi admin duyệt.'
    resetAccountRequestForm()
    await pollAccountRequestStatus()
    startAccountRequestPolling()
  } catch (err: any) {
    accountRequestError.value = err?.data?.detail || 'Gửi yêu cầu thất bại'
  } finally {
    isRequestLoading.value = false
  }
}
</script>

<template>
  <div v-if="showForgotPassword" class="relative flex min-h-screen items-center justify-center overflow-hidden bg-linear-to-br from-slate-50 via-blue-50 to-slate-100 p-4">
    <div class="pointer-events-none absolute -top-20 -left-20 h-52 w-52 rounded-full bg-blue-200/15 blur-3xl" />
    <div class="pointer-events-none absolute -right-24 -bottom-24 h-64 w-64 rounded-full bg-cyan-200/15 blur-3xl" />
    <div class="surface-card soft-enter card-hover w-full max-w-md p-8">
      <h2 class="text-center mb-6 font-bold text-2xl">Quên mật khẩu</h2>
      
      <div v-if="resetMessage" class="mb-4 rounded-xl border border-green-100 bg-green-50 px-4 py-3 text-green-700">
        {{ resetMessage }}
      </div>
      
      <form v-else @submit.prevent="handleForgotPassword">
        <div class="mb-4">
          <label for="email" class="block mb-2 font-medium">Email</label>
          <input
            type="email"
            id="email"
            v-model="email"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 transition focus:border-blue-400 focus:outline-none focus:ring-4 focus:ring-blue-100"
            required
          />
        </div>
        <button
          type="submit"
          class="mb-4 w-full rounded-xl bg-linear-to-r from-blue-600 to-cyan-600 px-4 py-2.5 font-bold text-white shadow-sm shadow-blue-200 transition hover:brightness-105"
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

  <div v-else-if="showAccountRequest" class="relative flex min-h-screen items-center justify-center overflow-hidden bg-linear-to-br from-slate-50 via-blue-50 to-slate-100 p-4">
    <div class="pointer-events-none absolute -top-20 -left-20 h-52 w-52 rounded-full bg-blue-200/15 blur-3xl" />
    <div class="pointer-events-none absolute -right-24 -bottom-24 h-64 w-64 rounded-full bg-cyan-200/15 blur-3xl" />
    <div class="surface-card soft-enter card-hover w-full max-w-md p-8">
      <div class="flex items-center justify-center mb-6">
        <div class="rounded-full bg-linear-to-r from-blue-600 to-cyan-600 p-3 shadow-sm shadow-blue-200">
          <UserPlus class="w-8 h-8 text-white" />
        </div>
      </div>

      <h2 class="text-center mb-2 font-bold text-2xl">Yêu cầu tạo tài khoản</h2>
      <p class="text-center text-gray-600 mb-6">Dành cho sinh viên và giáo viên chưa có tài khoản</p>

      <div v-if="accountRequestMessage" class="mb-4 rounded-xl border border-green-100 bg-green-50 px-4 py-3 text-green-700">
        {{ accountRequestMessage }}
      </div>

      <div v-if="accountCredentials" class="mb-4 rounded-xl border border-blue-100 bg-blue-50 px-4 py-4 text-blue-900">
        <p class="mb-3 font-semibold">Tài khoản của bạn đã sẵn sàng</p>
        <div class="space-y-2 font-mono text-sm">
          <p>Username: {{ accountCredentials.username }}</p>
          <p>Password: {{ accountCredentials.password }}</p>
        </div>
        <p class="mt-3 text-sm font-medium text-blue-700">
          Vui lòng ghi nhớ tài khoản và mật khẩu của bạn, đừng để nó đi lạc nha.
        </p>
      </div>

      <div v-if="accountRequestError" class="mb-4 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-red-600">
        {{ accountRequestError }}
      </div>

      <form v-if="!submittedRequestId" @submit.prevent="handleAccountRequest" class="space-y-4">
        <div>
          <label for="request-full-name" class="block mb-2 font-medium">Họ tên</label>
          <input
            id="request-full-name"
            v-model="accountRequestForm.fullName"
            type="text"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 transition focus:border-blue-400 focus:outline-none focus:ring-4 focus:ring-blue-100"
            required
            :disabled="isRequestLoading"
          />
        </div>

        <div>
          <label for="request-role" class="block mb-2 font-medium">Bạn là</label>
          <select
            id="request-role"
            v-model="accountRequestForm.role"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 transition focus:border-blue-400 focus:outline-none focus:ring-4 focus:ring-blue-100"
            :disabled="isRequestLoading"
          >
            <option value="student">Sinh viên</option>
            <option value="teacher">Giáo viên</option>
          </select>
        </div>

        <div>
          <label for="request-note" class="block mb-2 font-medium">Ghi chú</label>
          <textarea
            id="request-note"
            v-model="accountRequestForm.note"
            rows="3"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 transition focus:border-blue-400 focus:outline-none focus:ring-4 focus:ring-blue-100"
            placeholder="Ví dụ: lớp, khoa hoặc thông tin để admin xác nhận"
            :disabled="isRequestLoading"
          />
        </div>

        <button
          type="submit"
          class="w-full rounded-xl bg-linear-to-r from-blue-600 to-cyan-600 px-4 py-2.5 font-bold text-white shadow-sm shadow-blue-200 transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-70"
          :disabled="isRequestLoading"
        >
          {{ isRequestLoading ? 'Đang gửi...' : 'Gửi yêu cầu' }}
        </button>

        <button
          type="button"
          @click="showAccountRequest = false"
          class="w-full text-gray-600 hover:text-gray-800"
          :disabled="isRequestLoading"
        >
          Quay lại đăng nhập
        </button>
      </form>

      <button
        v-else
        type="button"
        @click="showAccountRequest = false"
        class="w-full text-gray-600 hover:text-gray-800"
      >
        Quay lại đăng nhập
      </button>
    </div>
  </div>

  <div v-else class="relative flex min-h-screen items-center justify-center overflow-hidden bg-linear-to-br from-slate-50 via-blue-50 to-slate-100 p-4">
    <div class="pointer-events-none absolute -top-20 -left-20 h-52 w-52 rounded-full bg-blue-200/15 blur-3xl" />
    <div class="pointer-events-none absolute -right-24 -bottom-24 h-64 w-64 rounded-full bg-cyan-200/15 blur-3xl" />
    <div class="surface-card soft-enter card-hover w-full max-w-md p-8">
      <div class="flex items-center justify-center mb-6">
        <div class="rounded-full bg-linear-to-r from-blue-600 to-cyan-600 p-3 shadow-sm shadow-blue-200">
          <LogIn class="w-8 h-8 text-white" />
        </div>
      </div>
      <h1 class="text-center mb-2 font-bold text-2xl">Hệ thống Thi trắc nghiệm</h1>
      <p class="text-center text-gray-600 mb-6">Đăng nhập để tiếp tục</p>

      <div v-if="error" class="mb-4 flex items-center gap-2 rounded-xl border border-red-100 bg-red-50 px-3 py-2.5 text-red-600">
        <span>⚠️</span> {{ error }}
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="mb-4">
          <label for="username" class="block mb-2 font-medium">Tên đăng nhập</label>
          <input
            type="text"
            id="username"
            v-model="username"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 transition focus:border-blue-400 focus:outline-none focus:ring-4 focus:ring-blue-100"
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
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 transition focus:border-blue-400 focus:outline-none focus:ring-4 focus:ring-blue-100"
            required
            :disabled="isLoading"
          />
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="mb-4 flex w-full items-center justify-center rounded-xl bg-linear-to-r from-blue-600 to-cyan-600 px-4 py-2.5 font-bold text-white shadow-sm shadow-blue-200 transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-70"
        >
          <span v-if="isLoading" class="mr-2 animate-spin">⚪</span>
          {{ isLoading ? 'Đang xử lý...' : 'Đăng nhập' }}
        </button>

        <button
          type="button"
          @click="showForgotPassword = true"
          class="mb-3 w-full text-blue-600 hover:text-blue-800 text-sm"
          :disabled="isLoading"
        >
          Quên mật khẩu?
        </button>
        <button
          type="button"
          @click="showAccountRequest = true"
          class="w-full rounded-xl border border-blue-100 bg-blue-50 px-4 py-2.5 font-medium text-blue-700 transition hover:bg-blue-100"
          :disabled="isLoading"
        >
          Chưa có tài khoản? Gửi yêu cầu cho admin
        </button>
      </form>

    </div>
  </div>
</template>
