<script setup lang="ts">
import { CheckCircle, Eye, X } from 'lucide-vue-next'
import type { ExamResult } from '~/types'

definePageMeta({ layout: 'student' })
const studentId = 'student1' // Mock

// Mock Data
const mockResults: ExamResult[] = [
  { id: 'r1', examId: 'exam1', studentId: 'student1', answers: [0, 2], score: 10, submittedAt: new Date('2024-02-01T08:30:00') },
  { id: 'r2', examId: 'exam2', studentId: 'student1', answers: [1], score: 7.5, submittedAt: new Date('2024-01-25T14:20:00') }
]
const mockExams = [{ id: 'exam1', title: 'Kiểm tra giữa kỳ', showAnswers: true }, { id: 'exam2', title: 'Bài tập tuần 5', showAnswers: false }]
const mockQuestions = [
  { id: 'q1', content: 'HTML là viết tắt?', options: ['A', 'B', 'C', 'D'], correctAnswer: 0 },
  { id: 'q2', content: 'CSS để làm gì?', options: ['A', 'B', 'C', 'D'], correctAnswer: 2 }
]

// State
const selectedResult = ref<ExamResult | null>(null)
const showAnswersModal = ref(false)
const studentResults = computed(() => mockResults.filter(r => r.studentId === studentId))

// Computed Stats
const avgScore = computed(() => studentResults.value.length ? (studentResults.value.reduce((s, r) => s + r.score, 0) / studentResults.value.length).toFixed(1) : 0)
const maxScore = computed(() => studentResults.value.length ? Math.max(...studentResults.value.map(r => r.score)) : 0)

const handleViewAnswers = (result: ExamResult) => {
  const exam = mockExams.find(e => e.id === result.examId)
  if (exam?.showAnswers) {
    selectedResult.value = result
    showAnswersModal.value = true
  } else {
    alert('Giảng viên chưa cho phép xem đáp án')
  }
}
</script>

<template>
  <div>
    <h2 class="mb-6 font-bold text-xl">Lịch sử thi</h2>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div class="bg-white p-6 rounded shadow"><p class="text-gray-500">Tổng bài thi</p><p class="text-3xl font-bold">{{ studentResults.length }}</p></div>
        <div class="bg-white p-6 rounded shadow"><p class="text-gray-500">Điểm TB</p><p class="text-3xl font-bold text-blue-600">{{ avgScore }}</p></div>
        <div class="bg-white p-6 rounded shadow"><p class="text-gray-500">Cao nhất</p><p class="text-3xl font-bold text-green-600">{{ maxScore }}</p></div>
    </div>

    <div v-if="studentResults.length === 0" class="bg-white p-12 text-center rounded shadow text-gray-500">Bạn chưa có bài thi nào</div>
    <div v-else class="bg-white rounded shadow overflow-hidden">
        <table class="w-full">
            <thead class="bg-gray-50 border-b">
                <tr><th class="p-4 text-left">Bài thi</th><th class="p-4 text-left">Điểm</th><th class="p-4 text-left">Ngày nộp</th><th class="p-4 text-right">Thao tác</th></tr>
            </thead>
            <tbody>
                <tr v-for="r in studentResults" :key="r.id" class="border-b hover:bg-gray-50">
                    <td class="p-4 flex items-center gap-2"><CheckCircle class="w-4 h-4 text-green-500"/> {{ mockExams.find(e => e.id === r.examId)?.title }}</td>
                    <td class="p-4"><span :class="['px-3 py-1 rounded-full text-sm font-bold', r.score >= 8 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">{{ r.score }}</span></td>
                    <td class="p-4">{{ r.submittedAt.toLocaleString('vi-VN') }}</td>
                    <td class="p-4 text-right">
                        <button v-if="mockExams.find(e => e.id === r.examId)?.showAnswers" @click="handleViewAnswers(r)" class="text-blue-600 flex items-center gap-1 justify-end w-full"><Eye class="w-4 h-4"/> Xem bài</button>
                        <span v-else class="text-gray-400 text-sm">Chưa mở</span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <div v-if="showAnswersModal && selectedResult" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
        <div class="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[80vh] overflow-y-auto">
            <div class="flex justify-between mb-4">
                 <h2 class="font-bold text-xl">Chi tiết bài làm</h2>
                 <button @click="showAnswersModal = false"><X class="w-5 h-5"/></button>
            </div>
            <div class="space-y-4">
                <div v-for="(q, idx) in mockQuestions" :key="q.id" class="border-b pb-4">
                    <p class="font-medium mb-2"><span :class="['px-2 rounded mr-2', selectedResult.answers[idx] === q.correctAnswer ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">Câu {{ idx + 1 }}</span> {{ q.content }}</p>
                    <div class="ml-10 space-y-1 text-sm">
                        <div v-for="(opt, i) in q.options" :key="i" :class="['p-2 rounded flex', i === q.correctAnswer ? 'bg-green-50 border border-green-200' : selectedResult.answers[idx] === i ? 'bg-red-50 border border-red-200' : 'bg-gray-50']">
                             <span class="mr-2 font-bold">{{ String.fromCharCode(65 + i) }}.</span> {{ opt }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>