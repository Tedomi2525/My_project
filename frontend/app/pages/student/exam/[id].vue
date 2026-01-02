<script setup lang="ts">
import { Clock, AlertCircle, CheckCircle, ArrowLeft, ArrowRight } from 'lucide-vue-next'
import type { Question } from '~/types'

definePageMeta({ layout: 'student' })
const route = useRoute()
const router = useRouter()
const examId = route.params.id as string

// Mock Data
const mockExams = [
  { id: 'exam1', title: 'Kiểm tra giữa kỳ - Lập trình Web', duration: 60, questions: ['q1', 'q2'], showAnswers: true },
  { id: 'exam2', title: 'Bài tập tuần 5', duration: 30, questions: ['q3'], showAnswers: false }
]
const allMockQuestions: Question[] = [
  { id: 'q1', content: 'HTML là viết tắt của gì?', options: ['Hyper Text Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlinks and Text Markup Language'], correctAnswer: 0, createdBy: 't1', createdAt: new Date() },
  { id: 'q2', content: 'CSS được sử dụng để làm gì?', options: ['Tạo cấu trúc trang web', 'Tạo hiệu ứng động', 'Tạo kiểu dáng cho trang web', 'Lưu trữ dữ liệu'], correctAnswer: 2, createdBy: 't1', createdAt: new Date() },
  { id: 'q3', content: 'JS là ngôn ngữ gì?', options: ['Biên dịch', 'Thông dịch', 'Máy', 'Assembly'], correctAnswer: 1, createdBy: 't1', createdAt: new Date() }
]

const mockExam = mockExams.find(e => e.id === examId)
const mockQuestions = allMockQuestions.filter(q => mockExam?.questions.includes(q.id))

// State
const started = ref(false)
const submitted = ref(false)
const currentQuestion = ref(0)
const answers = ref<number[]>(new Array(mockQuestions.length).fill(-1))
const timeLeft = ref(mockExam ? mockExam.duration * 60 : 0)
const showConfirmModal = ref(false)
const score = ref(0)
let timer: NodeJS.Timeout

// Timer Logic
onMounted(() => {
  if (!mockExam) return
})

// Watch started state to start timer
watch(started, (newValue) => {
  if (newValue && !submitted.value) {
    timer = setInterval(() => {
      if (timeLeft.value <= 1) {
        handleSubmit()
        clearInterval(timer)
        timeLeft.value = 0
      } else {
        timeLeft.value--
      }
    }, 1000)
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

// Actions
const handleAnswerSelect = (optIdx: number) => {
  answers.value[currentQuestion.value] = optIdx
}

const handleSubmit = () => {
  if (!submitted.value) {
    clearInterval(timer)
    let correctCount = 0
    mockQuestions.forEach((q, idx) => {
      if (answers.value[idx] === q.correctAnswer) correctCount++
    })
    score.value = (correctCount / mockQuestions.length) * 10
    submitted.value = true
    showConfirmModal.value = false
  }
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const nextQuestion = () => {
  if (currentQuestion.value < mockQuestions.length - 1) currentQuestion.value++
}
const prevQuestion = () => {
  if (currentQuestion.value > 0) currentQuestion.value--
}
</script>

<template>
  <div v-if="!mockExam" class="max-w-4xl mx-auto text-center py-8">
     <div class="bg-white rounded-lg shadow p-8">
        <h2 class="text-xl font-bold mb-4">Không tìm thấy bài thi</h2>
        <button @click="router.push('/student')" class="bg-blue-600 text-white px-6 py-2 rounded-lg">Quay lại</button>
     </div>
  </div>

  <div v-else-if="!started && !submitted" class="max-w-4xl mx-auto">
    <div class="bg-white rounded-lg shadow-lg p-8">
      <div class="text-center mb-8">
        <div class="inline-block p-4 bg-blue-100 rounded-full mb-4">
          <CheckCircle class="w-12 h-12 text-blue-600" />
        </div>
        <h1 class="mb-2 text-2xl font-bold">{{ mockExam.title }}</h1>
        <p class="text-gray-600">Vui lòng đọc kỹ hướng dẫn trước khi bắt đầu</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div class="bg-blue-50 rounded-lg p-4 text-center">
            <p class="text-gray-600">Số câu hỏi</p>
            <p class="text-3xl text-blue-600 font-bold">{{ mockQuestions.length }}</p>
        </div>
        <div class="bg-green-50 rounded-lg p-4 text-center">
            <p class="text-gray-600">Thời gian</p>
            <p class="text-3xl text-green-600 font-bold">{{ mockExam.duration }} phút</p>
        </div>
         <div class="bg-purple-50 rounded-lg p-4 text-center">
            <p class="text-gray-600">Điểm tối đa</p>
            <p class="text-3xl text-purple-600 font-bold">10</p>
        </div>
      </div>

      <button @click="started = true" class="w-full px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-lg font-bold">
        Bắt đầu làm bài
      </button>
    </div>
  </div>

  <div v-else-if="submitted" class="max-w-4xl mx-auto">
    <div class="bg-white rounded-lg shadow p-8 mb-6 text-center">
        <h2 class="mb-4 font-bold text-2xl">Đã nộp bài thành công!</h2>
        <div class="text-6xl mb-4">{{ score.value >= 8 ? '🎉' : score.value >= 5 ? '👍' : '📚' }}</div>
        <p class="text-gray-600 mb-2">Điểm số của bạn</p>
        <p :class="['text-6xl mb-6 font-bold', score.value >= 8 ? 'text-green-600' : score.value >= 5 ? 'text-blue-600' : 'text-orange-600']">{{ score.toFixed(1) }}</p>
        <button @click="router.push('/student/history')" class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">Xem lịch sử thi</button>
    </div>

    <div v-if="mockExam.showAnswers" class="bg-white rounded-lg shadow p-8">
        <h3 class="mb-6 font-bold text-xl">Đáp án chi tiết</h3>
        <div class="space-y-6">
            <div v-for="(q, idx) in mockQuestions" :key="q.id" class="border-b pb-6">
                <div class="flex items-start gap-3 mb-4">
                    <span :class="['px-3 py-1 rounded-full text-sm font-bold', answers[idx] === q.correctAnswer ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">Câu {{ idx + 1 }}</span>
                    <p class="flex-1 font-medium">{{ q.content }}</p>
                </div>
                <div class="ml-16 space-y-2">
                    <div v-for="(opt, i) in q.options" :key="i" 
                         :class="['p-3 rounded-lg flex', i === q.correctAnswer ? 'bg-green-50 border border-green-200' : answers[idx] === i && i !== q.correctAnswer ? 'bg-red-50 border border-red-200' : 'bg-gray-50']">
                        <span class="mr-2 font-bold">{{ String.fromCharCode(65 + i) }}.</span>
                        <span class="flex-1">{{ opt }}</span>
                        <span v-if="i === q.correctAnswer" class="text-green-600 ml-2">(Đáp án đúng)</span>
                        <span v-if="answers[idx] === i && i !== q.correctAnswer" class="text-red-600 ml-2">(Bạn chọn)</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
  </div>

  <div v-else class="flex gap-6">
    <div class="w-64 shrink-0">
        <div class="bg-white rounded-lg shadow p-6 sticky top-6">
            <div :class="['flex items-center gap-2 px-4 py-3 rounded-lg mb-4 font-bold text-xl', timeLeft < 300 ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700']">
                <Clock class="w-5 h-5" /> {{ formatTime(timeLeft) }}
            </div>
            <h3 class="mb-4 font-bold">Danh sách câu hỏi</h3>
            <div class="grid grid-cols-4 gap-2 mb-6">
                <button v-for="(_, i) in mockQuestions" :key="i" 
                        @click="currentQuestion = i"
                        :class="['aspect-square rounded-lg flex items-center justify-center font-medium', 
                                  currentQuestion === i ? 'bg-blue-600 text-white ring-2 ring-blue-300' : 
                                  answers[i] !== -1 ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600']">
                    {{ i + 1 }}
                </button>
            </div>
            <button @click="showConfirmModal = true" class="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 font-bold">Nộp bài</button>
        </div>
    </div>

    <div class="flex-1">
        <div v-if="timeLeft < 300" class="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6 flex gap-3 text-orange-700">
            <AlertCircle class="w-5 h-5" /> Sắp hết thời gian!
        </div>

        <div class="bg-white rounded-lg shadow p-8 mb-6">
            <div class="flex items-start gap-4 mb-6">
                <span class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg font-bold">Câu {{ currentQuestion + 1 }}/{{ mockQuestions.length }}</span>
                <h2 class="flex-1 text-lg font-medium">{{ mockQuestions[currentQuestion].content }}</h2>
            </div>
            <img v-if="mockQuestions[currentQuestion].imageUrl" :src="mockQuestions[currentQuestion].imageUrl" class="max-w-lg rounded-lg mb-6" />
            
            <div class="space-y-3">
                <label v-for="(opt, i) in mockQuestions[currentQuestion].options" :key="i" 
                       :class="['flex items-start gap-4 p-5 rounded-lg cursor-pointer transition-all border-2',
                                answers[currentQuestion] === i ? 'bg-blue-50 border-blue-500 shadow-md' : 'bg-gray-50 border-transparent hover:bg-gray-100']">
                    <input type="radio" :name="`q-${currentQuestion}`" :checked="answers[currentQuestion] === i" @change="handleAnswerSelect(i)" class="mt-1.5 w-5 h-5" />
                    <div class="flex-1">
                        <span class="font-bold mr-3">{{ String.fromCharCode(65 + i) }}.</span>
                        <span>{{ opt }}</span>
                    </div>
                </label>
            </div>
        </div>

        <div class="flex justify-between">
            <button @click="prevQuestion" :disabled="currentQuestion === 0" class="flex gap-2 items-center px-6 py-3 rounded-lg bg-white shadow disabled:opacity-50">
                <ArrowLeft class="w-5 h-5" /> Câu trước
            </button>
            <button @click="nextQuestion" :disabled="currentQuestion === mockQuestions.length - 1" class="flex gap-2 items-center px-6 py-3 rounded-lg bg-white shadow disabled:opacity-50">
                Câu sau <ArrowRight class="w-5 h-5" />
            </button>
        </div>
    </div>

    <div v-if="showConfirmModal" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
        <div class="bg-white rounded-lg p-8 w-full max-w-md">
            <h2 class="mb-4 font-bold text-xl">Xác nhận nộp bài</h2>
            <div class="mb-6">
                <p>Bạn đã trả lời <strong>{{ answers.filter(a => a !== -1).length }}/{{ mockQuestions.length }}</strong> câu hỏi.</p>
                <div v-if="answers.some(a => a === -1)" class="mt-2 bg-orange-50 border border-orange-200 p-3 rounded text-orange-700 flex gap-2">
                    <AlertCircle class="w-5 h-5" /> Còn <strong>{{ answers.filter(a => a === -1).length }}</strong> câu chưa làm.
                </div>
            </div>
            <div class="flex gap-3">
                <button @click="showConfirmModal = false" class="flex-1 py-3 border rounded-lg">Làm tiếp</button>
                <button @click="handleSubmit" class="flex-1 py-3 bg-green-600 text-white rounded-lg font-bold">Nộp bài</button>
            </div>
        </div>
    </div>
  </div>
</template>