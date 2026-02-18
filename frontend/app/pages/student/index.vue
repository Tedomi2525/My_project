<script setup lang="ts">
import { Clock, Lock, CheckCircle, X } from 'lucide-vue-next'
import type { Exam } from '~/types'
import { useExams } from '~/composables/useExams'
import { useAuth } from '~/composables/useAuth'

definePageMeta({ layout: 'student' })

const router = useRouter()
const config = useRuntimeConfig()

/* ================= STATE ================= */
const exams = ref<Exam[]>([])
const loading = ref(false)

const showPasswordModal = ref(false)
const selectedExam = ref<Exam | null>(null)
const password = ref('')
const error = ref('')
const { user, fetchUser } = useAuth()

/* ================= FETCH EXAMS ================= */
const loadExams = async () => {
  if (!user.value) return
  
  loading.value = true
  try {
    exams.value = await $fetch<Exam[]>('/exams/my-exams', {
      baseURL: config.public.apiBase,
      headers: {
        // Gửi ID để backend thực hiện get_current_student
        'x-user-id': String(user.value.id) 
      }
    })
  } catch (err) {
    console.error("Lỗi xác nhận sinh viên:", err)
  } finally {
    loading.value = false
  }
}

const initExams = async () => {
  if (!user.value) {
    await fetchUser()
  }
  await loadExams()
}

onMounted(initExams)

watch(
  () => user.value?.id,
  async (id, prevId) => {
    if (id && id !== prevId) {
      await loadExams()
    }
  }
)

/* ================= COMPUTED ================= */
const availableExams = computed(() =>
  exams.value.filter(exam => {
    const now = new Date()
    if (!exam.start_time || !exam.end_time) return false

    return (
      now >= new Date(exam.start_time) &&
      now <= new Date(exam.end_time)
    )
  })
)

/* ================= METHODS ================= */
const isExamAvailable = (exam: Exam) => {
  const now = new Date()
  return (
    exam.start_time &&
    exam.end_time &&
    now >= new Date(exam.start_time) &&
    now <= new Date(exam.end_time)
  )
}

const handleStartExam = (exam: Exam) => {
  if (exam.has_password) {
    selectedExam.value = exam
    password.value = ''
    error.value = ''
    showPasswordModal.value = true
  } else {
    router.push(`/student/exam/${exam.id}`)
  }
}

const handlePasswordSubmit = async () => {
  if (!selectedExam.value) return

  try {
    await $fetch(`/exams/${selectedExam.value.id}/check-password`, {
      method: 'POST',
      baseURL: config.public.apiBase,
      body: { password: password.value }
    })
    router.push(`/student/exam/${selectedExam.value.id}`)
  } catch {
    error.value = 'Mật khẩu không đúng!'
  }
}
</script>

<template>
  <div>
    <h2 class="mb-6 font-bold text-xl">Bài thi của bạn</h2>

    <div v-if="loading" class="flex justify-center p-12">
      <Loader2 class="w-8 h-8 animate-spin text-blue-600" />
    </div>

    <div v-else-if="availableExams.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-500">Bạn chưa có bài thi nào</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="exam in availableExams" :key="exam.id" class="bg-white rounded-lg shadow p-6">
        <div class="mb-4">
          <h3 class="mb-2 font-semibold text-lg">{{ exam.title }}</h3>
          <span v-if="exam.has_password" class="inline-flex items-center gap-1 text-sm text-orange-600 bg-orange-50 px-2 py-1 rounded">
            <Lock class="w-4 h-4" /> Có mật khẩu
          </span>
        </div>

        <div class="space-y-2 text-gray-600 mb-6 text-sm">
          <div class="flex items-center gap-2">
            <Clock class="w-4 h-4" />
            <span>Thời gian: {{ exam.duration_minutes }} phút</span>
          </div>
          <div class="flex items-center gap-2">
            <CheckCircle class="w-4 h-4" />
            <span>Số câu hỏi: {{ exam.exam_questions?.length || 0 }}</span>
          </div>
          <p v-if="exam.start_time">Mở: {{ new Date(exam.start_time).toLocaleString('vi-VN') }}</p>
          <p v-if="exam.end_time">Đóng: {{ new Date(exam.end_time).toLocaleString('vi-VN') }}</p>
        </div>

        <button
          v-if="isExamAvailable(exam)"
          @click="handleStartExam(exam)"
          class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Vào thi
        </button>
        <div v-else class="w-full px-4 py-2 bg-gray-100 text-gray-500 rounded-lg text-center font-medium">
          {{ (exam.start_time && new Date() < new Date(exam.start_time)) ? 'Chưa đến giờ thi' : 'Đã hết hạn' }}
        </div>
      </div>
    </div>

    <div v-if="showPasswordModal && selectedExam" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-bold text-lg">Nhập mật khẩu</h2>
          <button @click="showPasswordModal = false" class="p-1 hover:bg-gray-100 rounded transition-colors">
            <X class="w-5 h-5" />
          </button>
        </div>
        
        <div class="mb-4">
          <p class="text-gray-600 mb-1">Bài thi: <strong>{{ selectedExam.title }}</strong></p>
          <p class="text-sm text-gray-500">Vui lòng nhập mật khẩu để vào thi</p>
        </div>

        <form @submit.prevent="handlePasswordSubmit">
          <div class="mb-4">
            <label class="block mb-2 font-medium">Mật khẩu</label>
            <input
              type="password"
              v-model="password"
              @input="error = ''"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Nhập mật khẩu"
              autofocus
              required
            />
            <p v-if="error" class="text-red-600 text-sm mt-2">{{ error }}</p>
          </div>

          <div class="flex gap-3">
            <button type="button" @click="showPasswordModal = false" class="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50">Hủy</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Vào thi</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
