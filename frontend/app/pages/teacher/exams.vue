<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Search, Plus, Edit2, Trash2, Eye, EyeOff, Loader2 } from 'lucide-vue-next'
import type { Exam } from '~/types'
import { useExams } from '~/composables/useExams'
import { useAuth } from '~/composables/useAuth'

definePageMeta({
  layout: 'teacher'
})

/* ================= TYPES ================= */

interface Question {
  id: number
  content: string
}

interface ClassItem {
  id: number
  name: string
  code?: string
  student_count?: number
}

/* ================= AUTH ================= */

const { user, fetchUser } = useAuth()
const config = useRuntimeConfig()

/* ================= COMPOSABLE ================= */

const {
  exams,
  loading,
  getExams,
  getExamById,
  createExam,
  updateExam,
  deleteExam
} = useExams()

/* ================= STATE ================= */

const searchTerm = ref('')
const showModal = ref(false)
const isSubmitting = ref(false)
const editingExamId = ref<number | null>(null)

const availableQuestions = ref<Question[]>([])
const availableClasses = ref<ClassItem[]>([])
const isLoadingResources = ref(false)
const error = ref<string | null>(null)

/**
 * Form state
 * - questions + class_ids là nguồn sự thật
 * - KHÔNG reset khi EDIT
 */
const formData = ref({
  title: '',
  description: '',
  duration_minutes: 60,
  start_time: '',
  end_time: '',
  questions: [] as number[],
  class_ids: [] as number[],
  allow_view_answers: true,
  password: ''
})

/* ================= LOAD DATA ================= */

const loadPageData = async () => {
  if (!user.value) {
    await fetchUser()
  }
  if (!user.value) {
    error.value = 'Chua dang nhap hoac phien da het han'
    return
  }

  try {
    await getExams()

    isLoadingResources.value = true

    const headers = {
      'x-user-id': String(user.value.id)
    }

    const [qRes, cRes] = await Promise.all([
      $fetch<Question[]>('/questions', {
        baseURL: config.public.apiBase,
        headers
      }),
      $fetch<ClassItem[]>('/classes', {
        baseURL: config.public.apiBase,
        headers
      })
    ])

    availableQuestions.value = qRes || []
    availableClasses.value = cRes || []
  } catch (err) {
    error.value = 'Không tải được dữ liệu phụ'
    console.error(err)
  } finally {
    isLoadingResources.value = false
  }
}

onMounted(loadPageData)

watch(
  () => user.value?.id,
  async () => {
    await loadPageData()
  },
  { immediate: true }
)

/* ================= COMPUTED ================= */

const filteredExams = computed(() =>
  exams.value.filter(e =>
    e.title.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
)

/* ================= DATE HELPERS ================= */

const formatDateForInput = (dateStr: string | null) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
}

const formatDateDisplay = (dateStr: string | null) => {
  if (!dateStr) return 'Không xác định'
  return new Date(dateStr).toLocaleString('vi-VN')
}

/* ================= STATUS HELPERS ================= */

const getExamStatus = (exam: Exam) => {
  const now = new Date()
  const start = exam.start_time ? new Date(exam.start_time) : null
  const end = exam.end_time ? new Date(exam.end_time) : null

  if (!start || !end) return 'draft'
  if (now < start) return 'upcoming'
  if (now > end) return 'closed'
  return 'active'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    draft: 'Nháp',
    upcoming: 'Sắp diễn ra',
    active: 'Đang diễn ra',
    closed: 'Đã kết thúc'
  }
  return labels[status] || 'Không xác định'
}

const getStatusClasses = (status: string) => {
  const classes: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-800',
    upcoming: 'bg-blue-100 text-blue-800',
    active: 'bg-green-100 text-green-800',
    closed: 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

/* ================= METHODS ================= */

/**
 * ⚠️ CHỈ dùng cho CREATE
 */
const resetFormForCreate = () => {
  editingExamId.value = null
  formData.value = {
    title: '',
    description: '',
    duration_minutes: 60,
    start_time: '',
    end_time: '',
    questions: [],
    class_ids: [],
    allow_view_answers: true,
    password: ''
  }
}

const handleAddExam = () => {
  resetFormForCreate()
  showModal.value = true
}

const handleEditExam = async (exam: Exam) => {
  editingExamId.value = exam.id
  showModal.value = true

  try {
    const detail = await getExamById(exam.id)

    formData.value = {
      title: detail.title,
      description: detail.description || '',
      duration_minutes: detail.duration_minutes,
      start_time: formatDateForInput(detail.start_time),
      end_time: formatDateForInput(detail.end_time),

      // 🔥 luôn sync FULL list
      questions: [...(detail.exam_questions ?? [])],
      class_ids: [...(detail.allowed_classes ?? [])],

      allow_view_answers: detail.allow_view_answers ?? true,
      password: ''
    }
  } catch (err) {
    console.error(err)
    alert('Không lấy được chi tiết đề thi')
    showModal.value = false
  }
}

const handleDeleteExam = async (id: number) => {
  if (confirm('Bạn có chắc chắn muốn xóa đề thi này?')) {
    await deleteExam(id)
  }
}

const handleSubmit = async () => {
  if (isSubmitting.value) return

  try {
    isSubmitting.value = true
    console.log('SUBMIT QUESTIONS:', formData.value.questions)

    const payload: any = {
      title: formData.value.title,
      description: formData.value.description,
      duration_minutes: formData.value.duration_minutes,
      allow_view_answers: formData.value.allow_view_answers,
      class_ids: [...formData.value.class_ids],
      questions: [...formData.value.questions]
    }

    if (formData.value.start_time)
      payload.start_time = new Date(formData.value.start_time).toISOString()

    if (formData.value.end_time)
      payload.end_time = new Date(formData.value.end_time).toISOString()

    if (formData.value.password)
      payload.password = formData.value.password

    if (editingExamId.value) {
      await updateExam(editingExamId.value, payload)
      showModal.value = false
    } else {
      await createExam(payload)
      resetFormForCreate()
      showModal.value = false
    }

    await getExams()
  } catch (err: any) {
    alert(err.response?.data?.detail || err.message)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div>
    <div class="mb-6 flex flex-col sm:flex-row gap-4 justify-between">
      <div class="relative flex-1 max-w-md">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input type="text" placeholder="Tìm kiếm đề thi..." v-model="searchTerm"
          class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <button @click="handleAddExam"
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
        <Plus class="w-5 h-5" />
        Tạo đề thi mới
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-10">
      <Loader2 class="w-8 h-8 animate-spin text-blue-600" />
    </div>
    <div v-else-if="error" class="text-center text-red-500 py-10">
      {{ error }}
    </div>

    <div v-else class="space-y-4">
      <div v-for="exam in filteredExams" :key="exam.id" class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-start mb-4">
          <div>
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold">{{ exam.title }}</h3>
              <span :class="`px-3 py-1 rounded-full text-xs font-medium ${getStatusClasses(getExamStatus(exam))}`">
                {{ getStatusLabel(getExamStatus(exam)) }}
              </span>
            </div>
            <div class="text-sm text-gray-600 space-y-1">
              <p>Thời gian: {{ exam.duration_minutes }} phút</p>
              <p>
                Mở: {{ formatDateDisplay(exam.start_time) }} -
                Đóng: {{ formatDateDisplay(exam.end_time) }}
              </p>
              <p v-if="exam.has_password" class="text-amber-600 flex items-center gap-1 font-medium">
                Có mật khẩu bảo vệ
              </p>
            </div>
          </div>

          <div class="flex gap-2">
            <button @click="handleEditExam(exam)" class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg" title="Sửa">
              <Edit2 class="w-4 h-4" />
            </button>
            <button @click="handleDeleteExam(exam.id)" class="p-2 text-red-600 hover:bg-red-50 rounded-lg" title="Xóa">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div class="flex items-center gap-2 text-sm border-t pt-3 mt-3">
          <span v-if="exam.allow_view_answers" class="flex items-center gap-2 text-green-600">
            <Eye class="w-4 h-4" /> Xem đáp án: Có
          </span>
          <span v-else class="flex items-center gap-2 text-gray-600">
            <EyeOff class="w-4 h-4" /> Xem đáp án: Không
          </span>
        </div>
      </div>
    </div>

    <div v-if="showModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div class="bg-white rounded-lg p-6 w-full max-w-4xl my-8 max-h-[90vh] overflow-y-auto">
        <h2 class="mb-4 text-xl font-bold">
          {{ editingExamId ? 'Sửa đề thi' : 'Tạo đề thi mới' }}
        </h2>

        <form @submit.prevent="handleSubmit">
          <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="md:col-span-2">
                <label class="block mb-2 font-medium">Tên đề thi</label>
                <input type="text" v-model="formData.title"
                  class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" required />
              </div>
              <div class="md:col-span-2">
                <label class="block mb-2 font-medium">Mô tả</label>
                <textarea v-model="formData.description"
                  class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" rows="2"></textarea>
              </div>
              <div>
                <label class="block mb-2 font-medium">Thời gian (phút)</label>
                <input type="number" v-model.number="formData.duration_minutes"
                  class="w-full px-4 py-2 border rounded-lg" min="1" required />
              </div>
              <div>
                <label class="block mb-2 font-medium">Mật khẩu (để trống nếu không đổi)</label>
                <input type="text" v-model="formData.password" class="w-full px-4 py-2 border rounded-lg"
                  placeholder="***" />
              </div>
              <div>
                <label class="block mb-2 font-medium">Bắt đầu</label>
                <input type="datetime-local" v-model="formData.start_time" class="w-full px-4 py-2 border rounded-lg"
                  required />
              </div>
              <div>
                <label class="block mb-2 font-medium">Kết thúc</label>
                <input type="datetime-local" v-model="formData.end_time" class="w-full px-4 py-2 border rounded-lg"
                  required />
              </div>
              <div class="md:col-span-2">
                <label class="flex items-center gap-2">
                  <input type="checkbox" v-model="formData.allow_view_answers" class="w-4 h-4" />
                  Cho phép xem đáp án sau khi thi
                </label>
              </div>
            </div>

            <div>
              <label class="block mb-2 font-medium">Chọn câu hỏi ({{ formData.questions.length }} đã chọn)</label>

              <div v-if="isLoadingResources" class="text-sm text-gray-500">Đang tải danh sách câu hỏi...</div>

              <div v-else class="max-h-60 overflow-y-auto border rounded-lg p-4 space-y-2">
                <label v-for="(q, idx) in availableQuestions" :key="q.id"
                  class="flex items-start gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer">
                  <input type="checkbox" v-model="formData.questions" :value="q.id" class="mt-1" />
                  <div class="text-sm">
                    <span class="font-bold text-gray-600">#{{ q.id }}</span> {{ q.content }}
                  </div>
                </label>

                <div v-if="availableQuestions.length === 0" class="text-center text-gray-500 text-sm">
                  Chưa có câu hỏi nào trong ngân hàng đề.
                </div>
              </div>
            </div>

            <div>
              <label class="block mb-2 font-medium">
                Áp dụng cho lớp ({{ formData.class_ids.length }} đã chọn)
              </label>

              <div v-if="isLoadingResources" class="text-sm text-gray-500">
                <Loader2 class="w-4 h-4 animate-spin inline mr-2" /> Đang tải danh sách lớp...
              </div>

              <div v-else class="max-h-60 overflow-y-auto border rounded-lg p-4 space-y-2">
                <label v-for="cls in availableClasses" :key="cls.id"
                  class="flex items-center gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer transition-colors"
                  :class="{ 'bg-blue-50 border-blue-100': formData.class_ids.includes(cls.id) }">
                  <input type="checkbox" v-model="formData.class_ids" :value="cls.id"
                    class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500" />
                  <div class="flex-1">
                    <div class="flex justify-between items-center">
                      <p class="font-medium text-gray-900">{{ cls.name }}</p>
                      <span class="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                        {{ cls.code }}
                      </span>
                    </div>
                    <p v-if="cls.student_count !== undefined" class="text-gray-500 text-xs mt-0.5">
                      Sĩ số: {{ cls.student_count }} sinh viên
                    </p>
                  </div>
                </label>

                <div v-if="availableClasses.length === 0" class="text-center text-gray-500 text-sm py-4">
                  Không tìm thấy lớp học nào.
                </div>
              </div>
            </div>

            <div class="flex gap-3 mt-6">
              <button type="button" @click="showModal = false"
                class="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50">
                Hủy
              </button>
              <button type="submit" :disabled="isSubmitting"
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                <span v-if="isSubmitting">
                  <Loader2 class="w-4 h-4 animate-spin inline mr-2" />Đang xử lý...
                </span>
                <span v-else>{{ editingExamId ? 'Cập nhật' : 'Tạo đề thi' }}</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
