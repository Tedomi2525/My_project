<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Download, Edit2, Eye, Loader2, Trash2, X } from 'lucide-vue-next'
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
  difficulty?: string | null
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

interface QuestionAnalytics {
  question_id: number
  content: string
  difficulty: string | null
  total_answers: number
  correct_answers: number
  wrong_answers: number
  correct_rate: number
  wrong_rate: number
}

interface ExamSession {
  id?: number
  session_id?: number
  exam_id: number
  student_id: number
  violation_count: number
  started_at: string | null
  last_saved_at: string | null
}

const config = useRuntimeConfig()
const { user, fetchUser } = useAuth()
const tokenCookie = useCookie<string | null>('token')

const exams = ref<Exam[]>([])
const selectedExam = ref<number | null>(null)
const examResults = ref<TeacherResult[]>([])
const questionAnalytics = ref<QuestionAnalytics[]>([])
const examSessions = ref<ExamSession[]>([])

const loading = ref(true)
const loadingResults = ref(false)
const error = ref('')

const showAnswersModal = ref(false)
const loadingReview = ref(false)
const selectedReview = ref<ReviewPayload | null>(null)
const reviewError = ref('')
const loadingDifficultyStats = ref(false)
const loadingAnalytics = ref(false)

type DifficultyKey = 'EASY' | 'MEDIUM' | 'HARD'
type DifficultyStats = Record<DifficultyKey, { correct: number; total: number }>

const createEmptyDifficultyStats = (): DifficultyStats => ({
  EASY: { correct: 0, total: 0 },
  MEDIUM: { correct: 0, total: 0 },
  HARD: { correct: 0, total: 0 }
})

const difficultyStats = ref<DifficultyStats>(createEmptyDifficultyStats())

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
      label: 'Số sinh viên',
      data: distribution.map(d => d.count),
      backgroundColor: '#3b82f6'
    }]
  }
})

const pieChartData = computed(() => {
  const distribution = [
    { name: 'Giỏi (8-10)', value: examResults.value.filter(r => r.total_score >= 8).length, color: '#22c55e' },
    { name: 'Khá (6.5-8)', value: examResults.value.filter(r => r.total_score >= 6.5 && r.total_score < 8).length, color: '#3b82f6' },
    { name: 'TB (5-6.5)', value: examResults.value.filter(r => r.total_score >= 5 && r.total_score < 6.5).length, color: '#f59e0b' },
    { name: 'Yếu (<5)', value: examResults.value.filter(r => r.total_score < 5).length, color: '#ef4444' }
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

const difficultyChartData = computed(() => {
  const labels = ['Dễ', 'Trung bình', 'Khó']
  const keys: DifficultyKey[] = ['EASY', 'MEDIUM', 'HARD']
  const data = keys.map((key) => {
    const stat = difficultyStats.value[key]
    if (stat.total === 0) return 0
    return Number(((stat.correct / stat.total) * 100).toFixed(1))
  })

  return {
    labels,
    datasets: [
      {
        label: 'Tỷ lệ đúng (%)',
        data,
        backgroundColor: ['#22c55e', '#f59e0b', '#ef4444']
      }
    ]
  }
})

const difficultyChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      ticks: {
        callback: (value: number | string) => `${value}%`
      }
    }
  }
}

const difficultyRows = computed(() => {
  const rows: Array<{ key: DifficultyKey; label: string; correct: number; total: number; percent: string }> = [
    { key: 'EASY', label: 'Dễ', correct: 0, total: 0, percent: '0.0' },
    { key: 'MEDIUM', label: 'Trung bình', correct: 0, total: 0, percent: '0.0' },
    { key: 'HARD', label: 'Khó', correct: 0, total: 0, percent: '0.0' }
  ]

  return rows.map((row) => {
    const stat = difficultyStats.value[row.key]
    const percent = stat.total > 0 ? ((stat.correct / stat.total) * 100).toFixed(1) : '0.0'
    return {
      ...row,
      correct: stat.correct,
      total: stat.total,
      percent
    }
  })
})

const violationCountByStudent = computed(() => {
  const map = new Map<number, number>()
  for (const session of examSessions.value) {
    const current = map.get(session.student_id) || 0
    map.set(session.student_id, Math.max(current, Number(session.violation_count || 0)))
  }
  return map
})

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return 'Không xác định'
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

const normalizeDifficulty = (difficulty?: string | null): DifficultyKey => {
  if (!difficulty) return 'MEDIUM'
  const normalized = difficulty.toUpperCase()
  if (normalized === 'EASY' || normalized === 'MEDIUM' || normalized === 'HARD') {
    return normalized
  }
  return 'MEDIUM'
}

const headers = computed(() => ({
  Authorization: `Bearer ${tokenCookie.value || ''}`,
  'x-user-id': String(user.value?.id || ''),
  'x-user-role': String(user.value?.role || '')
}))

const loadDifficultyStats = async () => {
  difficultyStats.value = createEmptyDifficultyStats()

  if (!selectedExam.value || examResults.value.length === 0) return

  loadingDifficultyStats.value = true
  try {
    const reviews = await Promise.all(
      examResults.value.map((result) =>
        $fetch<ReviewPayload>(`/results/${result.id}/review`, {
          baseURL: config.public.apiBase,
          headers: headers.value
        })
      )
    )

    const nextStats = createEmptyDifficultyStats()
    reviews.forEach((review) => {
      review.questions.forEach((question) => {
        const key = normalizeDifficulty(question.difficulty)
        nextStats[key].total += 1
        if (question.is_correct) nextStats[key].correct += 1
      })
    })

    difficultyStats.value = nextStats
  } catch (err) {
    console.error('Lỗi tải thống kê độ khó:', err)
  } finally {
    loadingDifficultyStats.value = false
  }
}

const loadQuestionAnalytics = async () => {
  questionAnalytics.value = []
  examSessions.value = []
  if (!selectedExam.value) return

  loadingAnalytics.value = true
  try {
    const [analyticsRes, sessionsRes] = await Promise.all([
      $fetch<QuestionAnalytics[]>(`/results/exam/${selectedExam.value}/question-analytics`, {
        baseURL: config.public.apiBase,
        headers: headers.value
      }),
      $fetch<ExamSession[]>(`/exams/${selectedExam.value}/sessions`, {
        baseURL: config.public.apiBase,
        headers: headers.value
      })
    ])
    questionAnalytics.value = analyticsRes || []
    examSessions.value = sessionsRes || []
  } catch (err) {
    console.error('Lỗi tải phân tích câu hỏi/log vi phạm:', err)
  } finally {
    loadingAnalytics.value = false
  }
}

const loadExams = async () => {
  try {
    const data = await $fetch<Exam[]>('/exams', {
      baseURL: config.public.apiBase,
      headers: headers.value
    })
    exams.value = data || []
    selectedExam.value = exams.value[0]?.id ?? null
  } catch (err) {
    console.error('Lỗi tải danh sách đề thi:', err)
    error.value = 'Không tải được danh sách đề thi'
  }
}

const loadExamResults = async () => {
  if (!selectedExam.value) {
    examResults.value = []
    difficultyStats.value = createEmptyDifficultyStats()
    return
  }
  if (!exams.value.some(exam => exam.id === selectedExam.value)) {
    examResults.value = []
    difficultyStats.value = createEmptyDifficultyStats()
    return
  }

  loadingResults.value = true
  difficultyStats.value = createEmptyDifficultyStats()
  try {
    const data = await $fetch<TeacherResult[]>(`/results/exam/${selectedExam.value}`, {
      baseURL: config.public.apiBase,
      headers: headers.value
    })
    examResults.value = data || []
    await loadDifficultyStats()
    await loadQuestionAnalytics()
  } catch (err) {
    console.error('Lỗi tải kết quả đề thi:', err)
    error.value = 'Không tải được kết quả đề thi'
    examResults.value = []
  } finally {
    loadingResults.value = false
  }
}

const handleUpdateScore = async (result: TeacherResult) => {
  const raw = prompt('Nhập điểm mới từ 0 đến 10', result.total_score.toString())
  if (raw == null) return

  const score = Number(raw)
  if (Number.isNaN(score) || score < 0 || score > 10) {
    alert('Điểm phải là số từ 0 đến 10')
    return
  }

  try {
    await $fetch(`/results/${result.id}/score`, {
      method: 'PUT',
      query: { score },
      baseURL: config.public.apiBase,
      headers: headers.value
    })
    await loadExamResults()
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || 'Không cập nhật được điểm')
  }
}

const handleDeleteResult = async (result: TeacherResult) => {
  if (!confirm(`Xóa kết quả của ${result.student_name}?`)) return

  try {
    await $fetch(`/results/${result.id}`, {
      method: 'DELETE',
      baseURL: config.public.apiBase,
      headers: headers.value
    })
    await loadExamResults()
  } catch (err: any) {
    alert(err?.data?.detail || err?.message || 'Không xóa được kết quả')
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
    console.error('Lỗi tải chi tiết bài làm:', err)
    reviewError.value = err?.data?.detail || 'Không tải được chi tiết bài làm'
  } finally {
    loadingReview.value = false
  }
}

const handleExportExcel = () => {
  const csv = examResults.value.map((result, idx) => {
    return `${idx + 1},${result.student_code || ''},${result.student_name},${result.total_score.toFixed(2)},${formatDate(result.finished_at)}`
  }).join('\n')

  const blob = new Blob([`STT,Mã SV,Họ tên,Điểm,Thời gian nộp\n${csv}`], { type: 'text/csv;charset=utf-8;' })
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
      error.value = 'Không xác định được tài khoản giáo viên'
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
        <label class="block mb-2 font-medium">Chọn đề thi</label>
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
          <p class="text-gray-600 mb-2">Số thí sinh</p>
          <p class="text-3xl font-bold">{{ examResults.length }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-gray-600 mb-2">Điểm trung bình</p>
          <p class="text-3xl font-bold text-blue-600">{{ avgScore }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-gray-600 mb-2">Điểm cao nhất</p>
          <p class="text-3xl font-bold text-green-600">{{ maxScore }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <p class="text-gray-600 mb-2">Điểm thấp nhất</p>
          <p class="text-3xl font-bold text-red-600">{{ minScore }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="mb-4 font-bold text-lg">Phân bố điểm</h3>
          <div class="h-72">
            <Bar :data="barChartData" :options="chartOptions" />
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="mb-4 font-bold text-lg">Phân loại học lực</h3>
          <div class="h-72">
            <Pie :data="pieChartData" :options="chartOptions" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h3 class="mb-4 font-bold text-lg">Tỷ lệ trả lời đúng theo độ khó</h3>
        <div v-if="loadingDifficultyStats" class="flex justify-center py-8">
          <Loader2 class="w-6 h-6 animate-spin text-blue-600" />
        </div>
        <div v-else class="space-y-4">
          <div class="h-72">
            <Bar :data="difficultyChartData" :options="difficultyChartOptions" />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div v-for="row in difficultyRows" :key="row.key" class="rounded-lg border border-gray-200 p-3 text-sm">
              <p class="font-semibold mb-1">{{ row.label }}</p>
              <p>Đúng: {{ row.correct }}/{{ row.total }}</p>
              <p>Tỷ lệ: {{ row.percent }}%</p>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h3 class="mb-4 font-bold text-lg">Phân tích từng câu hỏi</h3>
        <div v-if="loadingAnalytics" class="flex justify-center py-8">
          <Loader2 class="w-6 h-6 animate-spin text-blue-600" />
        </div>
        <div v-else-if="questionAnalytics.length === 0" class="text-gray-500 text-center py-6">
          Chưa có dữ liệu phân tích câu hỏi.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left">Câu hỏi</th>
                <th class="px-4 py-3 text-left">Độ khó</th>
                <th class="px-4 py-3 text-right">Tổng lượt trả lời</th>
                <th class="px-4 py-3 text-right">Đúng</th>
                <th class="px-4 py-3 text-right">Sai</th>
                <th class="px-4 py-3 text-right">Tỷ lệ sai</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="item in questionAnalytics" :key="item.question_id">
                <td class="px-4 py-3 max-w-lg">{{ item.content }}</td>
                <td class="px-4 py-3">{{ item.difficulty || '-' }}</td>
                <td class="px-4 py-3 text-right">{{ item.total_answers }}</td>
                <td class="px-4 py-3 text-right text-green-700">{{ item.correct_answers }}</td>
                <td class="px-4 py-3 text-right text-red-700">{{ item.wrong_answers }}</td>
                <td class="px-4 py-3 text-right font-semibold">
                  {{ (item.wrong_rate * 100).toFixed(1) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="p-6 border-b border-gray-200 flex justify-between items-center">
          <h3 class="font-bold text-lg">Bảng điểm chi tiết</h3>
          <button
            @click="handleExportExcel"
            class="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Download class="w-5 h-5" />
            Xuất CSV
          </button>
        </div>

        <div v-if="loadingResults" class="flex justify-center py-8">
          <Loader2 class="w-6 h-6 animate-spin text-blue-600" />
        </div>

        <div v-else-if="examResults.length === 0" class="p-8 text-center text-gray-500">
          Chưa có kết quả cho đề thi này.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left">STT</th>
                <th class="px-6 py-3 text-left">Mã SV</th>
                <th class="px-6 py-3 text-left">Họ tên</th>
                <th class="px-6 py-3 text-left">Điểm</th>
                <th class="px-6 py-3 text-left">Vi phạm</th>
                <th class="px-6 py-3 text-left">Thời gian nộp</th>
                <th class="px-6 py-3 text-right">Thao tác</th>
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
                <td class="px-6 py-4">
                  {{ violationCountByStudent.get(result.student_id) || 0 }}
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
                      Xem đáp án
                    </button>
                    <button
                      @click="handleUpdateScore(result)"
                      class="flex items-center gap-2 px-3 py-2 text-amber-700 hover:bg-amber-50 rounded-lg transition-colors"
                    >
                      <Edit2 class="w-4 h-4" />
                      Sửa điểm
                    </button>
                    <button
                      @click="handleDeleteResult(result)"
                      class="flex items-center gap-2 px-3 py-2 text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 class="w-4 h-4" />
                      Xóa
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <div v-if="showAnswersModal && selectedReview" class="modal-overlay z-100 items-start pt-16 sm:pt-20 overflow-y-auto">
      <div class="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[88vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold">
            Chi tiết bài làm - {{ selectedReview.exam_title }}
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
                <span v-if="key === q.correct_answer" class="ml-2 text-green-700 font-medium">(Đáp án đúng)</span>
                <span v-if="key === q.student_answer && key !== q.correct_answer" class="ml-2 text-red-700 font-medium">(Đã chọn)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

