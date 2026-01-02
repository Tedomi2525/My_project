<script setup lang="ts">
import { Clock, Lock, CheckCircle, X } from 'lucide-vue-next'
import type { Exam } from '~/types'

definePageMeta({ layout: 'student' })
const router = useRouter()
const studentId = 'student1' // Mock ID

// Mock Data
const mockExams: Exam[] = [
  {
    id: 'exam1', title: 'Kiểm tra giữa kỳ - Lập trình Web', duration: 60,
    startTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    endTime: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    questions: ['q1', 'q2'], allowedStudents: ['student1', 'student2'],
    status: 'active', showAnswers: true, createdBy: 'teacher1', password: 'web123'
  },
  {
    id: 'exam2', title: 'Bài tập tuần 5', duration: 30,
    startTime: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    endTime: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
    questions: ['q3'], allowedStudents: ['student1', 'student2', 'student3'],
    status: 'active', showAnswers: false, createdBy: 'teacher1'
  }
]

// State
const showPasswordModal = ref(false)
const selectedExam = ref<Exam | null>(null)
const password = ref('')
const error = ref('')

const availableExams = computed(() => 
  mockExams.filter(exam => exam.allowedStudents.includes(studentId) && exam.status === 'active')
)

const isExamAvailable = (exam: Exam) => {
  const now = new Date()
  return now >= new Date(exam.startTime) && now <= new Date(exam.endTime)
}

const handleStartExam = (exam: Exam) => {
  if (exam.password) {
    selectedExam.value = exam
    password.value = ''
    error.value = ''
    showPasswordModal.value = true
  } else {
    router.push(`/student/exam/${exam.id}`)
  }
}

const handlePasswordSubmit = () => {
  if (selectedExam.value && password.value === selectedExam.value.password) {
    router.push(`/student/exam/${selectedExam.value.id}`)
  } else {
    error.value = 'Mật khẩu không đúng!'
  }
}
</script>

<template>
  <div>
    <h2 class="mb-6 font-bold text-xl">Bài thi của bạn</h2>

    <div v-if="availableExams.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-500">Bạn chưa có bài thi nào</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="exam in availableExams" :key="exam.id" class="bg-white rounded-lg shadow p-6">
        <div class="mb-4">
          <h3 class="mb-2 font-semibold text-lg">{{ exam.title }}</h3>
          <span v-if="exam.password" class="inline-flex items-center gap-1 text-sm text-orange-600 bg-orange-50 px-2 py-1 rounded">
            <Lock class="w-4 h-4" /> Có mật khẩu
          </span>
        </div>

        <div class="space-y-2 text-gray-600 mb-6 text-sm">
          <div class="flex items-center gap-2">
            <Clock class="w-4 h-4" />
            <span>Thời gian: {{ exam.duration }} phút</span>
          </div>
          <div class="flex items-center gap-2">
            <CheckCircle class="w-4 h-4" />
            <span>Số câu hỏi: {{ exam.questions.length }}</span>
          </div>
          <p>Mở: {{ new Date(exam.startTime).toLocaleString('vi-VN') }}</p>
          <p>Đóng: {{ new Date(exam.endTime).toLocaleString('vi-VN') }}</p>
        </div>

        <button
          v-if="isExamAvailable(exam)"
          @click="handleStartExam(exam)"
          class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Vào thi
        </button>
        <div v-else class="w-full px-4 py-2 bg-gray-100 text-gray-500 rounded-lg text-center font-medium">
          {{ new Date() < new Date(exam.startTime) ? 'Chưa đến giờ thi' : 'Đã hết hạn' }}
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
        
        <div class="mt-4 p-3 bg-blue-50 rounded-lg text-sm text-blue-700">
           💡 Mật khẩu demo: <code class="bg-blue-100 px-2 py-1 rounded font-mono font-bold">web123</code>
        </div>
      </div>
    </div>
  </div>
</template>