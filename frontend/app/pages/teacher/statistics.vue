<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Download, Eye, Loader2, X } from 'lucide-vue-next'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement
} from 'chart.js'
import { Bar, Pie } from 'vue-chartjs'
import type { Exam } from '~/types'
import { useAuth } from '~/composables/useAuth'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement)

definePageMeta({
  layout: 'teacher'
})

interface TeacherResult {
  id: number
  exam_id: number
  student_id: number
  student_name: string
  student_code: string
  total_score: number
  started_at: string | null
  finished_at: string | null
}

interface ReviewQuestion {
  question_id: number
  content: string
  options: Record<string, string> | null
  correct_answer: string
  student_answer: string
  is_correct: boolean
}

interface ReviewPayload {
  result_id: number
  exam_id: number
  exam_title: string
  student_id: number
  total_score: number
  started_at: string | null
  finished_at: string | null
  allow_view_answers: boolean
  questions: ReviewQuestion[]
}

const config = useRuntimeConfig()
const { user, fetchUser } = useAuth()

const exams = ref<Exam[]>([])
const selectedExam = ref<number | null>(null)
const examResults = ref<TeacherResult[]>([])

const loading = ref(true)
const loadingResults = ref(false)
const error = ref('')

const showAnswersModal = ref(false)
const loadingReview = ref(false)
const selectedReview = ref<ReviewPayload | null>(null)
const reviewError = ref('')

const avgScore = computed(() => {
  if (examResults.value.length === 0) return '0.00'
  const sum = examResults.value.reduce((acc, r) => acc + r.total_score, 0)
  return (sum / examResults.value.length).toFixed(2)
})

const maxScore = computed(() =>
  examResults.value.length > 0 ? Math.max(...examResults.value.map(r => r.total_score)) : 0
)

const minScore = computed(() =>
  examResults.value.length > 0 ? Math.min(...examResults.value.map(r => r.total_score)) : 0
)

const barChartData = computed(() => {
  const distribution = [
    { range: '0-2.9', count: examResults.value.filter(r => r.total_score < 3).length },
    { range: '3-4.9', count: examResults.value.filter(r => r.total_score >= 3 && r.total_score < 5).length },
    { range: '5-6.9', count: examResults.value.filter(r => r.total_score >= 5 && r.total_score < 7).length },
    { range: '7-8.9', count: examResults.value.filter(r => r.total_score >= 7 && r.total_score < 9).length },
    { range: '9-10', count: examResults.value.filter(r => r.total_score >= 9).length }
  ]

  return {
    labels: distribution.map(d => d.range),
    datasets: [{
      label: 'So sinh vien',
      data: distribution.map(d => d.count),
      backgroundColor: '#3b82f6'
    }]
  }
})

const pieChartData = computed(() => {
  const distribution = [
    { name: 'Gioi (8-10)', value: examResults.value.filter(r => r.total_score >= 8).length, color: '#22c55e' },
    { name: 'Kha (6.5-8)', value: examResults.value.filter(r => r.total_score >= 6.5 && r.total_score < 8).length, color: '#3b82f6' },
    { name: 'TB (5-6.5)', value: examResults.value.filter(r => r.total_score >= 5 && r.total_score < 6.5).length, color: '#f59e0b' },
    { name: 'Yeu (<5)', value: examResults.value.filter(r => r.total_score < 5).length, color: '#ef4444' }
  ]

  return {
    labels: distribution.map(d => d.name),
    datasets: [{
      data: distribution.map(d => d.value),
      backgroundColor: distribution.map(d => d.color)
    }]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false
}

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return 'Khong xac dinh'
  return new Date(dateStr).toLocaleString('vi-VN')
}

const getScoreColorClass = (score: number) => {
  if (score >= 8) return 'bg-green-100 text-green-700'
  if (score >= 6.5) return 'bg-blue-100 text-blue-700'
  if (score >= 5) return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
}

const optionEntries = (options: Record<string, string> | null) => {
  if (!options) return [] as Array<[string, string]>
  return Object.entries(options)
}

const headers = computed(() => ({
  'x-user-id': String(user.value?.id || '')
}))

const loadExams = async () => {
  try {
    const data = await $fetch<Exam[]>('/exams', {
      baseURL: config.public.apiBase,
      headers: headers.value
    })
    exams.value = data || []
    selectedExam.value = exams.value.length > 0 ? exams.value[0].id : null
  } catch (err) {
    console.error('Loi tai danh sach de thi:', err)
    error.value = 'Khong tai duoc danh sach de thi'
  }
}

const loadExamResults = async () => {
  if (!selectedExam.value) {
    examResults.value = []
    return
  }
  if (!exams.value.some(exam => exam.id === selectedExam.value)) {
    examResults.value = []
    return
  }

  loadingResults.value = true
  try {
    const data = await $fetch<TeacherResult[]>(`/results/exam/${selectedExam.value}`, {
      baseURL: config.public.apiBase,
      headers: headers.value
    })
    examResults.value = data || []
  } catch (err) {
    console.error('Loi tai ket qua de thi:', err)
    error.value = 'Khong tai duoc ket qua de thi'
    examResults.value = []
  } finally {
    loadingResults.value = false
  }
}

const handleViewAnswers = async (resultId: number) => {
  loadingReview.value = true
  reviewError.value = ''

  try {
    const review = await $fetch<ReviewPayload>(`/results/${resultId}/review`, {
      baseURL: config.public.apiBase,
      headers: headers.value
    })
    selectedReview.value = review
    showAnswersModal.value = true
  } catch (err: any) {
    console.error('Loi tai chi tiet bai lam:', err)
    reviewError.value = err?.data?.detail || 'Khong tai duoc chi tiet bai lam'
  } finally {
    loadingReview.value = false
  }
}

const handleExportExcel = () => {
  const csv = examResults.value.map((result, idx) => {
    return `${idx + 1},${result.student_code || ''},${result.student_name},${result.total_score.toFixed(2)},${formatDate(result.finished_at)}`
  }).join('\n')

  const blob = new Blob([`STT,Ma SV,Ho ten,Diem,Thoi gian nop\n${csv}`], { type: 'text/csv;charset=utf-8;' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `bang_diem_exam_${selectedExam.value || 'unknown'}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}

onMounted(async () => {
  loading.value = true
  error.value = ''

  try {
    if (!user.value) await fetchUser()
    if (!user.value) {
      error.value = 'Khong xac dinh duoc tai khoan giao vien'
      return
    }

    await loadExams()
    await loadExamResults()
  } finally {
    loading.value = false
  }
})

watch(selectedExam, async () => {
  await loadExamResults()
})
</script>

<template>
  <div>
    <div v-if="loading" class="flex justify-center py-12">
      <Loader2 class="w-8 h-8 animate-spin text-blue-600" />
    </div>

    <div v-else-if="error && exams.length === 0" class="bg-white rounded-lg shadow p-6 text-red-600 text-center">
      {{ error }}
    </div>

    <template v-else>
      <div class="mb-6 bg-white rounded-lg shadow p-6">
        <label class="block mb-2 font-medium">Chon de thi</label>
        <select
          v-model="selectedExam"
          class="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option v-for="exam in exams" :key="exam.id" :value="exam.id">
            {{ exam.title }}
          </option>
        </select>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-gray-600 mb-2">So thi sinh</p>
          <p class="text-3xl font-bold">{{ examResults.length }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-gray-600 mb-2">Diem trung binh</p>
          <p class="text-3xl font-bold text-blue-600">{{ avgScore }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-gray-600 mb-2">Diem cao nhat</p>
          <p class="text-3xl font-bold text-green-600">{{ maxScore }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-gray-600 mb-2">Diem thap nhat</p>
          <p class="text-3xl font-bold text-red-600">{{ minScore }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="mb-4 font-bold text-lg">Pho diem</h3>
          <div class="h-72">
            <Bar :data="barChartData" :options="chartOptions" />
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="mb-4 font-bold text-lg">Phan loai hoc luc</h3>
          <div class="h-72">
            <Pie :data="pieChartData" :options="chartOptions" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="p-6 border-b border-gray-200 flex justify-between items-center">
          <h3 class="font-bold text-lg">Bang diem chi tiet</h3>
          <button
            @click="handleExportExcel"
            class="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Download class="w-5 h-5" />
            Xuat CSV
          </button>
        </div>

        <div v-if="loadingResults" class="flex justify-center py-8">
          <Loader2 class="w-6 h-6 animate-spin text-blue-600" />
        </div>

        <div v-else-if="examResults.length === 0" class="p-8 text-center text-gray-500">
          Chua co ket qua cho de thi nay.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left">STT</th>
                <th class="px-6 py-3 text-left">Ma SV</th>
                <th class="px-6 py-3 text-left">Ho ten</th>
                <th class="px-6 py-3 text-left">Diem</th>
                <th class="px-6 py-3 text-left">Thoi gian nop</th>
                <th class="px-6 py-3 text-right">Thao tac</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="(result, idx) in examResults" :key="result.id" class="hover:bg-gray-50">
                <td class="px-6 py-4">{{ idx + 1 }}</td>
                <td class="px-6 py-4">{{ result.student_code || '-' }}</td>
                <td class="px-6 py-4">{{ result.student_name }}</td>
                <td class="px-6 py-4">
                  <span :class="`px-3 py-1 rounded-full text-sm ${getScoreColorClass(result.total_score)}`">
                    {{ result.total_score.toFixed(2) }}
                  </span>
                </td>
                <td class="px-6 py-4">{{ formatDate(result.finished_at) }}</td>
                <td class="px-6 py-4">
                  <div class="flex gap-2 justify-end">
                    <button
                      @click="handleViewAnswers(result.id)"
                      :disabled="loadingReview"
                      class="flex items-center gap-2 px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
                    >
                      <Eye class="w-4 h-4" />
                      Xem dap an
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <div v-if="showAnswersModal && selectedReview" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[88vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold">
            Chi tiet bai lam - {{ selectedReview.exam_title }}
          </h2>
          <button @click="showAnswersModal = false" class="p-1 hover:bg-gray-100 rounded">
            <X class="w-5 h-5" />
          </button>
        </div>

        <p v-if="reviewError" class="mb-4 text-red-600 text-sm">{{ reviewError }}</p>

        <div class="space-y-5">
          <div
            v-for="(q, idx) in selectedReview.questions"
            :key="q.question_id"
            class="border rounded-lg p-4"
          >
            <div class="flex items-start gap-2 mb-3">
              <span class="font-semibold">Cau {{ idx + 1 }}:</span>
              <p class="flex-1">{{ q.content }}</p>
            </div>

            <div class="space-y-2">
              <div
                v-for="([key, value], optIdx) in optionEntries(q.options)"
                :key="key"
                :class="[
                  'p-3 rounded border text-sm',
                  key === q.correct_answer
                    ? 'bg-green-50 border-green-200'
                    : key === q.student_answer
                      ? 'bg-red-50 border-red-200'
                      : 'bg-gray-50 border-gray-200'
                ]"
              >
                <span class="font-semibold mr-2">{{ String.fromCharCode(65 + optIdx) }}.</span>
                <span>{{ value }}</span>
                <span v-if="key === q.correct_answer" class="ml-2 text-green-700 font-medium">(Dap an dung)</span>
                <span v-if="key === q.student_answer && key !== q.correct_answer" class="ml-2 text-red-700 font-medium">(Da chon)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
