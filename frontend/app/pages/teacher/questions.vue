<script setup lang="ts">
import { Search, Plus, Edit2, Trash2, Image as ImageIcon } from 'lucide-vue-next'
import type { Question } from '~/types'

definePageMeta({ layout: 'teacher' })
const teacherId = 'teacher1'

// Mock Data
const initialQuestions: Question[] = [
  { id: 'q1', content: 'HTML là viết tắt của gì?', options: ['Hyper Text Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlinks and Text Markup Language'], correctAnswer: 0, createdBy: 'teacher1', createdAt: new Date('2024-01-15') },
  { id: 'q2', content: 'CSS được sử dụng để làm gì?', options: ['Tạo cấu trúc trang web', 'Tạo hiệu ứng động', 'Tạo kiểu dáng cho trang web', 'Lưu trữ dữ liệu'], correctAnswer: 2, createdBy: 'teacher1', createdAt: new Date('2024-01-16') },
]

// State
const questions = ref<Question[]>(initialQuestions)
const searchTerm = ref('')
const showModal = ref(false)
const editingQuestion = ref<Question | null>(null)
const formData = reactive({
  content: '',
  imageUrl: '',
  options: ['', '', '', ''],
  correctAnswer: 0
})

const filteredQuestions = computed(() => 
  questions.value.filter(q => q.content.toLowerCase().includes(searchTerm.value.toLowerCase()))
)

// Actions
const resetForm = () => {
    Object.assign(formData, { content: '', imageUrl: '', options: ['', '', '', ''], correctAnswer: 0 })
}

const handleAddQuestion = () => {
  editingQuestion.value = null
  resetForm()
  showModal.value = true
}

const handleEditQuestion = (question: Question) => {
  editingQuestion.value = question
  Object.assign(formData, {
      content: question.content,
      imageUrl: question.imageUrl || '',
      options: [...question.options],
      correctAnswer: question.correctAnswer
  })
  showModal.value = true
}

const handleDeleteQuestion = (id: string) => {
  if (confirm('Bạn có chắc chắn muốn xóa?')) questions.value = questions.value.filter(q => q.id !== id)
}

const handleSubmit = () => {
  if (editingQuestion.value) {
    questions.value = questions.value.map(q => q.id === editingQuestion.value?.id ? { ...q, ...formData } : q)
  } else {
    questions.value.push({
      id: `q_${Date.now()}`,
      ...formData,
      createdBy: teacherId,
      createdAt: new Date()
    })
  }
  showModal.value = false
}
</script>

<template>
  <div>
    <div class="mb-6 flex justify-between gap-4">
       <div class="relative flex-1 max-w-md">
         <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
         <input type="text" v-model="searchTerm" placeholder="Tìm câu hỏi..." class="w-full pl-10 pr-4 py-2 border rounded-lg" />
       </div>
       <button @click="handleAddQuestion" class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
         <Plus class="w-5 h-5" /> Thêm câu hỏi
       </button>
    </div>

    <div class="space-y-4">
      <div v-for="(q, idx) in filteredQuestions" :key="q.id" class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-start mb-4">
          <div class="flex-1">
             <div class="flex gap-3">
                <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm h-fit">Câu {{ idx + 1 }}</span>
                <div class="flex-1">
                    <p>{{ q.content }}</p>
                    <img v-if="q.imageUrl" :src="q.imageUrl" class="mt-3 max-w-xs rounded-lg border" />
                </div>
             </div>
          </div>
          <div class="flex gap-2">
             <button @click="handleEditQuestion(q)" class="p-2 text-blue-600 bg-blue-50 rounded"><Edit2 class="w-4 h-4" /></button>
             <button @click="handleDeleteQuestion(q.id)" class="p-2 text-red-600 bg-red-50 rounded"><Trash2 class="w-4 h-4" /></button>
          </div>
        </div>
        <div class="ml-16 space-y-2">
            <div v-for="(opt, i) in q.options" :key="i" :class="['p-3 rounded-lg', i === q.correctAnswer ? 'bg-green-50 border border-green-200' : 'bg-gray-50']">
                <span class="font-bold mr-2">{{ String.fromCharCode(65 + i) }}.</span> {{ opt }}
                <span v-if="i === q.correctAnswer" class="ml-2 text-green-600 text-sm font-semibold">(Đáp án đúng)</span>
            </div>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 overflow-y-auto">
        <div class="bg-white rounded-lg p-6 w-full max-w-2xl my-8">
            <h2 class="font-bold text-xl mb-4">{{ editingQuestion ? 'Sửa câu hỏi' : 'Thêm câu hỏi' }}</h2>
            <form @submit.prevent="handleSubmit" class="space-y-4">
                <div>
                    <label class="block mb-1">Nội dung</label>
                    <textarea v-model="formData.content" rows="3" class="w-full border p-2 rounded" required></textarea>
                </div>
                <div>
                    <label class="block mb-1">Ảnh URL</label>
                    <input type="url" v-model="formData.imageUrl" class="w-full border p-2 rounded" />
                </div>
                <div>
                    <label class="block mb-1">Phương án</label>
                    <div v-for="(opt, i) in formData.options" :key="i" class="flex gap-2 mb-2">
                        <span class="p-2 bg-gray-100 rounded w-8 text-center">{{ String.fromCharCode(65 + i) }}</span>
                        <input type="text" v-model="formData.options[i]" class="flex-1 border p-2 rounded" required />
                    </div>
                </div>
                <div>
                    <label class="block mb-1">Đáp án đúng</label>
                    <select v-model="formData.correctAnswer" class="w-full border p-2 rounded">
                        <option v-for="(opt, i) in formData.options" :key="i" :value="i">Phương án {{ String.fromCharCode(65 + i) }}</option>
                    </select>
                </div>
                <div class="flex gap-3 pt-4">
                    <button type="button" @click="showModal = false" class="flex-1 border py-2 rounded">Hủy</button>
                    <button type="submit" class="flex-1 bg-blue-600 text-white py-2 rounded">Lưu</button>
                </div>
            </form>
        </div>
    </div>
  </div>
</template>