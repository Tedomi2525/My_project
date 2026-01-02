<script setup lang="ts">
import { Download, Eye } from 'lucide-vue-next'
import type { ExamResult } from '~/types'

definePageMeta({ layout: 'teacher' })

const mockExams = [{ id: 'exam1', title: 'Kiểm tra giữa kỳ' }]
const mockResults: ExamResult[] = [
  { id: 'r1', examId: 'exam1', studentId: 's1', answers: [0, 2], score: 5, submittedAt: new Date() },
  { id: 'r2', examId: 'exam1', studentId: 's2', answers: [0, 2], score: 9, submittedAt: new Date() },
  { id: 'r3', examId: 'exam1', studentId: 's3', answers: [0, 2], score: 7.5, submittedAt: new Date() },
]
const mockStudents = [{ id: 's1', name: 'Nguyễn Văn A', studentId: 'SV01' }, { id: 's2', name: 'Trần B', studentId: 'SV02' }, { id: 's3', name: 'Lê C', studentId: 'SV03' }]

const selectedExam = ref('exam1')
const showAnswersModal = ref(false)
const selectedResult = ref<ExamResult | null>(null)

const examResults = computed(() => mockResults.filter(r => r.examId === selectedExam.value))

// Tính toán đơn giản
const avgScore = computed(() => examResults.value.length ? (examResults.value.reduce((a, b) => a + b.score, 0) / examResults.value.length).toFixed(2) : 0)
const maxScore = computed(() => Math.max(...examResults.value.map(r => r.score)))

// Dữ liệu cho biểu đồ (CSS-based)
const scoreRanges = computed(() => {
    const ranges = [0,0,0,0] // <5, 5-7, 7-9, >9
    examResults.value.forEach(r => {
        if(r.score < 5) ranges[0]++
        else if(r.score < 7) ranges[1]++
        else if(r.score < 9) ranges[2]++
        else ranges[3]++
    })
    return ranges
})
</script>

<template>
  <div>
    <div class="mb-6 bg-white p-6 rounded shadow">
        <label>Chọn đề thi: </label>
        <select v-model="selectedExam" class="border p-2 rounded ml-2">
            <option v-for="e in mockExams" :key="e.id" :value="e.id">{{ e.title }}</option>
        </select>
    </div>

    <div class="grid grid-cols-4 gap-6 mb-6">
        <div class="bg-white p-6 rounded shadow text-center">
            <p class="text-gray-500">Số thí sinh</p>
            <p class="text-3xl font-bold">{{ examResults.length }}</p>
        </div>
        <div class="bg-white p-6 rounded shadow text-center">
            <p class="text-gray-500">Điểm TB</p>
            <p class="text-3xl font-bold text-blue-600">{{ avgScore }}</p>
        </div>
        <div class="bg-white p-6 rounded shadow text-center">
            <p class="text-gray-500">Cao nhất</p>
            <p class="text-3xl font-bold text-green-600">{{ maxScore }}</p>
        </div>
    </div>

    <div class="bg-white p-6 rounded shadow mb-6">
        <h3 class="font-bold mb-4">Phổ điểm</h3>
        <div class="flex items-end justify-around h-40 gap-4">
            <div v-for="(count, idx) in scoreRanges" :key="idx" class="w-full flex flex-col items-center">
                <div class="w-full bg-blue-500 rounded-t transition-all duration-500" :style="{ height: `${count * 20 + 5}%` }"></div>
                <p class="mt-2 text-sm">{{ ['<5', '5-7', '7-9', '>9'][idx] }}</p>
                <p class="font-bold">{{ count }} SV</p>
            </div>
        </div>
    </div>

    <div class="bg-white rounded shadow overflow-hidden">
        <table class="w-full">
            <thead class="bg-gray-50 border-b">
                <tr>
                    <th class="p-4 text-left">SV</th>
                    <th class="p-4 text-left">Điểm</th>
                    <th class="p-4 text-right">Thao tác</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="r in examResults" :key="r.id" class="border-b hover:bg-gray-50">
                    <td class="p-4">{{ mockStudents.find(s => s.id === r.studentId)?.name }}</td>
                    <td class="p-4 font-bold">{{ r.score }}</td>
                    <td class="p-4 text-right">
                        <button @click="selectedResult = r; showAnswersModal = true" class="text-blue-600 flex items-center gap-1 justify-end w-full">
                            <Eye class="w-4 h-4" /> Xem bài
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <div v-if="showAnswersModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div class="bg-white p-6 rounded w-96">
            <h3 class="font-bold text-lg mb-4">Kết quả chi tiết</h3>
            <p>Sinh viên: {{ mockStudents.find(s => s.id === selectedResult?.studentId)?.name }}</p>
            <p>Điểm: {{ selectedResult?.score }}</p>
            <div class="mt-6 text-right">
                <button @click="showAnswersModal = false" class="bg-blue-600 text-white px-4 py-2 rounded">Đóng</button>
            </div>
        </div>
    </div>
  </div>
</template>