<script setup lang="ts">
import { Search, Plus, Edit2, Trash2 } from 'lucide-vue-next'
import type { Question } from '~/types'

definePageMeta({ layout: 'teacher' })

/* ================= AUTH ================= */
const { user } = useAuth()
const config = useRuntimeConfig()

/* ================= STATE ================= */
const questions = ref<Question[]>([])
const loading = ref(false)
const searchTerm = ref('')

const showModal = ref(false)
const editingQuestion = ref<Question | null>(null)

/* ================= FORM ================= */
const formData = reactive({
  content: '',
  question_type: 'MCQ',
  options: {
    A: '',
    B: '',
    C: '',
    D: ''
  } as Record<string, string>,
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
  api<Question>('/questions', {
    method: 'POST',
    body: payload
  })

const updateQuestion = (id: number, payload: any) =>
  api<Question>(`/questions/${id}`, {
    method: 'PUT',
    body: payload
  })

const deleteQuestion = (id: number) =>
  api(`/questions/${id}`, { method: 'DELETE' })

/* ================= COMPUTED ================= */
const filteredQuestions = computed(() =>
  questions.value.filter(q =>
    q.content.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
)

/* ================= ACTIONS ================= */
const resetForm = () => {
  formData.content = ''
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
  formData.options = { ...q.options }
  formData.correct_answer = q.correct_answer
  showModal.value = true
}

const handleSubmit = async () => {
  const payload = {
    content: formData.content,
    question_type: 'MCQ',
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

/* ================= LOAD ================= */
onMounted(fetchQuestions)
</script>

<template>
  <div>
    <!-- SEARCH + ADD -->
    <div class="mb-6 flex justify-between gap-4">
      <div class="relative flex-1 max-w-md">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          v-model="searchTerm"
          placeholder="Tìm câu hỏi..."
          class="w-full pl-10 pr-4 py-2 border rounded-lg"
        />
      </div>

      <button
        @click="openCreate"
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg"
      >
        <Plus class="w-5 h-5" />
        Thêm câu hỏi
      </button>
    </div>

    <!-- LIST -->
    <div v-if="loading" class="text-gray-500">Đang tải...</div>

    <div v-else class="space-y-4">
      <div
        v-for="(q, idx) in filteredQuestions"
        :key="q.id"
        class="bg-white rounded-lg shadow p-6"
      >
        <div class="flex justify-between mb-4">
          <div>
            <span class="text-sm text-gray-500">Câu {{ idx + 1 }}</span>
            <p class="font-medium mt-1">{{ q.content }}</p>
          </div>

          <div class="flex gap-2">
            <button @click="openEdit(q)" class="p-2 text-blue-600 bg-blue-50 rounded">
              <Edit2 class="w-4 h-4" />
            </button>
            <button @click="handleDelete(q.id)" class="p-2 text-red-600 bg-red-50 rounded">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- OPTIONS -->
        <div class="space-y-2">
          <div
            v-for="(text, key) in q.options"
            :key="key"
            :class="[
              'p-3 rounded-lg',
              key === q.correct_answer
                ? 'bg-green-50 border border-green-200'
                : 'bg-gray-50'
            ]"
          >
            <b>{{ key }}.</b> {{ text }}
            <span
              v-if="key === q.correct_answer"
              class="ml-2 text-green-600 text-sm"
            >
              (Đáp án đúng)
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-xl">
        <h2 class="font-bold text-xl mb-4">
          {{ editingQuestion ? 'Sửa câu hỏi' : 'Thêm câu hỏi' }}
        </h2>

        <div class="space-y-4">
          <textarea
            v-model="formData.content"
            rows="3"
            class="w-full border p-2 rounded"
            placeholder="Nội dung câu hỏi"
          />

          <div v-for="key in ['A','B','C','D']" :key="key" class="flex gap-2">
            <span class="w-8 text-center font-bold">{{ key }}</span>
            <input
              v-model="formData.options[key]"
              class="flex-1 border p-2 rounded"
              placeholder="Nhập đáp án"
            />
          </div>

          <select
            v-model="formData.correct_answer"
            class="w-full border p-2 rounded"
          >
            <option v-for="key in ['A','B','C','D']" :key="key" :value="key">
              Đáp án {{ key }}
            </option>
          </select>

          <div class="flex gap-3 pt-4">
            <button @click="showModal = false" class="flex-1 border py-2 rounded">
              Hủy
            </button>
            <button @click="handleSubmit" class="flex-1 bg-blue-600 text-white py-2 rounded">
              Lưu
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
