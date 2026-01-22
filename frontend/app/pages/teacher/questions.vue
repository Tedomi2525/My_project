<script setup lang="ts">
import { Search, Plus, Edit2, Trash2, Filter } from 'lucide-vue-next'
import type { Question } from '~/types'

definePageMeta({ layout: 'teacher' })

/* ================= AUTH ================= */
const { user } = useAuth()
const config = useRuntimeConfig()

/* ================= STATE ================= */
const questions = ref<Question[]>([])
const loading = ref(false)
const searchTerm = ref('')

// 1. THÊM STATE CHO BỘ LỌC
const selectedDifficulty = ref('ALL') // Mặc định chọn tất cả

const showModal = ref(false)
const editingQuestion = ref<Question | null>(null)

/* ================= FORM ================= */
const formData = reactive({
  content: '',
  question_type: 'MCQ',
  difficulty: 'EASY',
  options: { A: '', B: '', C: '', D: '' } as Record<string, string>,
  correct_answer: 'A'
})

/* ================= API ================= */
const api = <T>(url: string, options: any = {}) =>
  $fetch<T>(url, {
    baseURL: config.public.apiBase,
    ...options
  })

const fetchQuestions = async () => {
  loading.value = true
  try {
    questions.value = await api<Question[]>('/questions')
  } finally {
    loading.value = false
  }
}

const createQuestion = (payload: any) =>
  api<Question>('/questions', { method: 'POST', body: payload })

const updateQuestion = (id: number, payload: any) =>
  api<Question>(`/questions/${id}`, { method: 'PUT', body: payload })

const deleteQuestion = (id: number) =>
  api(`/questions/${id}`, { method: 'DELETE' })

/* ================= COMPUTED ================= */
// 2. CẬP NHẬT LOGIC LỌC
const filteredQuestions = computed(() =>
  questions.value.filter(q => {
    // Lọc theo từ khóa tìm kiếm
    const matchesSearch = q.content.toLowerCase().includes(searchTerm.value.toLowerCase())
    
    // Lọc theo độ khó
    const matchesDifficulty = selectedDifficulty.value === 'ALL' || q.difficulty === selectedDifficulty.value

    return matchesSearch && matchesDifficulty
  })
)

/* ================= HELPERS ================= */
const getDiffColor = (level: string) => {
  switch (level) {
    case 'HARD': return 'bg-red-100 text-red-700 border-red-200'
    case 'MEDIUM': return 'bg-yellow-100 text-yellow-700 border-yellow-200'
    default: return 'bg-green-100 text-green-700 border-green-200'
  }
}

const getDiffLabel = (level: string) => {
  const map: Record<string, string> = { EASY: 'Dễ', MEDIUM: 'Trung bình', HARD: 'Khó' }
  return map[level] || 'Dễ'
}

/* ================= ACTIONS ================= */
const resetForm = () => {
  formData.content = ''
  formData.difficulty = 'EASY'
  formData.options = { A: '', B: '', C: '', D: '' }
  formData.correct_answer = 'A'
}

const openCreate = () => {
  editingQuestion.value = null
  resetForm()
  showModal.value = true
}

const openEdit = (q: Question) => {
  editingQuestion.value = q
  formData.content = q.content
  formData.difficulty = q.difficulty || 'EASY'
  formData.options = { ...q.options }
  formData.correct_answer = q.correct_answer
  showModal.value = true
}

const handleSubmit = async () => {
  const payload = {
    content: formData.content,
    question_type: 'MCQ',
    difficulty: formData.difficulty,
    options: formData.options,
    correct_answer: formData.correct_answer,
    created_by: user.value!.id
  }

  if (editingQuestion.value) {
    await updateQuestion(editingQuestion.value.id, payload)
  } else {
    await createQuestion(payload)
  }

  showModal.value = false
  await fetchQuestions()
}

const handleDelete = async (id: number) => {
  if (!confirm('Bạn có chắc muốn xóa câu hỏi này?')) return
  await deleteQuestion(id)
  await fetchQuestions()
}

onMounted(fetchQuestions)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap gap-4 items-center">
      <div class="relative flex-1 min-w-50">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          v-model="searchTerm"
          placeholder="Tìm câu hỏi..."
          class="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
        />
      </div>

      <div class="relative w-48">
        <Filter class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <select 
          v-model="selectedDifficulty" 
          class="w-full pl-9 pr-4 py-2 border rounded-lg bg-white outline-none cursor-pointer focus:ring-2 focus:ring-blue-500 appearance-none"
        >
          <option value="ALL">Tất cả độ khó</option>
          <option value="EASY">Dễ</option>
          <option value="MEDIUM">Trung bình</option>
          <option value="HARD">Khó</option>
        </select>
        <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
        </div>
      </div>

      <button
        @click="openCreate"
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        <Plus class="w-5 h-5" />
        <span class="hidden sm:inline">Thêm câu hỏi</span>
      </button>
    </div>

    <div v-if="loading" class="text-center py-8 text-gray-500">
        <div class="animate-spin inline-block w-6 h-6 border-2 border-current border-t-transparent rounded-full mb-2"></div>
        <p>Đang tải dữ liệu...</p>
    </div>

    <div v-else-if="filteredQuestions.length === 0" class="text-center py-10 bg-gray-50 rounded-lg border border-dashed">
        <p class="text-gray-500">Không tìm thấy câu hỏi nào phù hợp.</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="(q, idx) in filteredQuestions"
        :key="q.id"
        class="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition"
      >
        <div class="flex justify-between items-start mb-4">
          <div>
            <div class="flex items-center gap-2 mb-2">
              <span class="text-sm font-semibold text-gray-500 bg-gray-100 px-2 py-0.5 rounded">#{{ q.id }}</span>
              <span 
                class="text-xs px-2 py-0.5 rounded border font-medium"
                :class="getDiffColor(q.difficulty)"
              >
                {{ getDiffLabel(q.difficulty) }}
              </span>
            </div>
            <p class="font-medium text-lg text-gray-800">{{ q.content }}</p>
          </div>

          <div class="flex gap-2">
            <button @click="openEdit(q)" class="p-2 text-blue-600 bg-blue-50 hover:bg-blue-100 rounded transition" title="Sửa">
              <Edit2 class="w-4 h-4" />
            </button>
            <button @click="handleDelete(q.id)" class="p-2 text-red-600 bg-red-50 hover:bg-red-100 rounded transition" title="Xóa">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div
            v-for="(text, key) in q.options"
            :key="key"
            :class="[
              'p-3 rounded-lg border text-sm',
              key === q.correct_answer
                ? 'bg-green-50 border-green-200 text-green-800'
                : 'bg-white border-gray-200 text-gray-600'
            ]"
          >
            <span class="font-bold mr-1">{{ key }}.</span> {{ text }}
            <span v-if="key === q.correct_answer" class="ml-2 text-xs font-bold text-green-600 uppercase tracking-wider border border-green-200 px-1 rounded">Đúng</span>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="showModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 backdrop-blur-sm"
    >
      <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-xl max-h-[90vh] overflow-y-auto">
        <h2 class="font-bold text-xl mb-6 flex items-center gap-2">
             <span class="bg-blue-100 text-blue-600 p-1 rounded"><Plus v-if="!editingQuestion" class="w-5 h-5"/><Edit2 v-else class="w-5 h-5"/></span>
             {{ editingQuestion ? 'Sửa câu hỏi' : 'Thêm câu hỏi mới' }}
        </h2>

        <div class="space-y-5">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700">Nội dung câu hỏi</label>
            <textarea
                v-model="formData.content"
                rows="3"
                class="w-full border border-gray-300 p-2.5 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="Nhập nội dung câu hỏi..."
            />
          </div>
          
          <div class="flex gap-4">
            <div class="w-1/3">
              <label class="block text-sm font-medium mb-1 text-gray-700">Độ khó</label>
              <select v-model="formData.difficulty" class="w-full border border-gray-300 p-2.5 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none bg-white">
                <option value="EASY">Dễ</option>
                <option value="MEDIUM">Trung bình</option>
                <option value="HARD">Khó</option>
              </select>
            </div>
             <div class="flex-1">
              <label class="block text-sm font-medium mb-1 text-gray-700">Đáp án đúng</label>
              <select
                v-model="formData.correct_answer"
                class="w-full border border-gray-300 p-2.5 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none bg-white"
              >
                <option v-for="key in ['A','B','C','D']" :key="key" :value="key">
                  Đáp án {{ key }}
                </option>
              </select>
            </div>
          </div>

          <div class="space-y-3 bg-gray-50 p-4 rounded-lg border">
            <label class="block text-sm font-semibold text-gray-700">Các lựa chọn</label>
            <div v-for="key in ['A','B','C','D']" :key="key" class="flex gap-3 items-center">
                <div class="w-8 h-8 flex items-center justify-center rounded-full bg-white border border-gray-200 font-bold text-gray-600 text-sm shadow-sm">{{ key }}</div>
                <input
                v-model="formData.options[key]"
                class="flex-1 border border-gray-300 p-2 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                :placeholder="`Nhập nội dung đáp án ${key}`"
                />
            </div>
          </div>

          <div class="flex gap-3 pt-2 border-t mt-4">
            <button @click="showModal = false" class="flex-1 py-2.5 rounded-lg border border-gray-300 font-medium hover:bg-gray-50 transition">
              Hủy bỏ
            </button>
            <button @click="handleSubmit" class="flex-1 bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition shadow-sm shadow-blue-200">
              {{ editingQuestion ? 'Cập nhật' : 'Tạo mới' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>