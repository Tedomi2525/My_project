<script setup lang="ts">
import { CheckCircle, CircleCheck, CircleX, Eye, EyeOff, Loader2, X } from 'lucide-vue-next'
import type { Exam, ExamResult } from '~/types'
import { useAuth } from '~/composables/useAuth'

definePageMeta({ layout: 'student' })

const config = useRuntimeConfig()
const { user, fetchUser } = useAuth()
const tokenCookie = useCookie<string | null>('token')

const results = ref<ExamResult[]>([])
const exams = ref<Exam[]>([])
const analytics = ref<StudentExamAnalytics[]>([])
const loading = ref(true)
const error = ref('')
const loadingReview = ref(false)
const showReviewModal = ref(false)
const reviewError = ref('')

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

interface StudentAnalyticsBucket {
  key: string
  label: string
  correct: number
  total: number
  correct_rate: number
}

interface StudentExamAnalytics {
  result_id: number
  exam_id: number
  exam_title: string
  student_id: number
  student_name: string
  student_code: string
  total_score: number
  correct_answers: number
  total_questions: number
  correct_rate: number
  by_topic: StudentAnalyticsBucket[]
  by_difficulty: StudentAnalyticsBucket[]
}

const selectedReview = ref<ReviewPayload | null>(null)

const studentResults = computed(() =>
  [...results.value].sort((a, b) => {
    const aTime = a.finished_at ? new Date(a.finished_at).getTime() : 0
    const bTime = b.finished_at ? new Date(b.finished_at).getTime() : 0
    return bTime - aTime
  })
)

const examMap = computed(() => new Map(exams.value.map(exam => [exam.id, exam])))
const analyticsByResult = computed(() => new Map(analytics.value.map(item => [item.result_id, item])))

const avgScore = computed(() => {
  if (!studentResults.value.length) return '0.0'
  const sum = studentResults.value.reduce((acc, r) => acc + r.total_score, 0)
  return (sum / studentResults.value.length).toFixed(1)
})

const maxScore = computed(() => {
  if (!studentResults.value.length) return 0
  return Math.max(...studentResults.value.map(r => r.total_score))
})

const analyticsRows = computed(() =>
  studentResults.value
    .map(result => analyticsByResult.value.get(result.id))
    .filter(Boolean) as StudentExamAnalytics[]
)

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return 'Không xác định'
  return new Date(dateStr).toLocaleString('vi-VN')
}

const examTitle = (examId: number) => {
  return examMap.value.get(examId)?.title || `Đề #${examId}`
}

const canViewAnswers = (examId: number) => {
  return !!examMap.value.get(examId)?.allow_view_answers
}

const optionEntries = (options: Record<string, string> | null) => {
  if (!options) return [] as Array<[string, string]>
  return Object.entries(options)
}

const parseAnswerKeys = (value?: string) => {
  return (value || '')
    .split(',')
    .map((item) => item.trim().toUpperCase())
    .filter(Boolean)
}

const hasAnswerKey = (value: string | undefined, key: string) => {
  return parseAnswerKeys(value).includes(key)
}

const difficultyLabel = (difficulty: string) => {
  const labels: Record<string, string> = {
    EASY: 'Dễ',
    MEDIUM: 'Trung bình',
    HARD: 'Khó',
    UNKNOWN: 'Không rõ'
  }
  return labels[difficulty] || difficulty
}

const loadReview = async (resultId: number) => {
  if (!user.value) return

  loadingReview.value = true
  reviewError.value = ''

  try {
    const review = await $fetch<ReviewPayload>(`/results/${resultId}/review`, {
      baseURL: config.public.apiBase,
      headers: {
        Authorization: `Bearer ${tokenCookie.value || ''}`
      }
    })

    selectedReview.value = review
    showReviewModal.value = true
  } catch (err: any) {
    console.error('Lỗi tải chi tiết bài làm:', err)
    reviewError.value = err?.data?.detail || 'Không tải được chi tiết bài làm'
  } finally {
    loadingReview.value = false
  }
}

const loadHistory = async () => {
  loading.value = true
  error.value = ''

  try {
    if (!user.value) {
      await fetchUser()
    }

    if (!user.value) {
      error.value = 'Không xác định được tài khoản sinh viên'
      return
    }

    const headers = {
      Authorization: `Bearer ${tokenCookie.value || ''}`
    }

    const [historyRes, examsRes] = await Promise.all([
      $fetch<ExamResult[]>(`/results/student/${user.value.id}`, {
        baseURL: config.public.apiBase,
        headers
      }),
      $fetch<Exam[]>('/exams/my-exams', {
        baseURL: config.public.apiBase,
        headers
      })
    ])

    results.value = historyRes || []
    exams.value = examsRes || []

    try {
      analytics.value = await $fetch<StudentExamAnalytics[]>(`/results/student/${user.value.id}/analytics`, {
        baseURL: config.public.apiBase,
        headers
      })
    } catch (analyticsErr) {
      console.error('Lỗi tải phân tích kết quả:', analyticsErr)
      analytics.value = []
    }
  } catch (err) {
    console.error('Lỗi tải lịch sử thi:', err)
    error.value = 'Không tải được lịch sử thi'
  } finally {
    loading.value = false
  }
}

onMounted(loadHistory)
</script>

<template>
  <div>
    <h2 class="mb-6 font-bold text-xl">Lịch sử thi</h2>

    <div v-if="loading" class="flex justify-center p-12">
      <Loader2 class="w-8 h-8 animate-spin text-blue-600" />
    </div>

    <div v-else-if="error" class="bg-white p-6 text-center rounded shadow text-red-600">
      {{ error }}
    </div>

    <template v-else>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div class="bg-white p-6 rounded shadow">
          <p class="text-gray-500">Tổng bài thi</p>
          <p class="text-3xl font-bold">{{ studentResults.length }}</p>
        </div>
        <div class="bg-white p-6 rounded shadow">
          <p class="text-gray-500">Điểm TB</p>
          <p class="text-3xl font-bold text-blue-600">{{ avgScore }}</p>
        </div>
        <div class="bg-white p-6 rounded shadow">
          <p class="text-gray-500">Cao nhất</p>
          <p class="text-3xl font-bold text-green-600">{{ maxScore }}</p>
        </div>
      </div>

      <div v-if="studentResults.length === 0" class="bg-white p-12 text-center rounded shadow text-gray-500">
        Bạn chưa có bài thi nào
      </div>

      <div v-else class="bg-white rounded shadow p-6 mb-6">
        <h3 class="mb-4 font-bold text-lg">Phân tích kết quả của bạn</h3>
        <div v-if="analyticsRows.length === 0" class="text-gray-500 text-center py-6">
          Chưa có dữ liệu phân tích.
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="item in analyticsRows"
            :key="item.result_id"
            class="rounded-lg border border-gray-200 p-4"
          >
            <div class="mb-4 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h4 class="font-semibold text-gray-900">{{ examTitle(item.exam_id) }}</h4>
                <p class="text-sm text-gray-500">
                  Đúng {{ item.correct_answers }}/{{ item.total_questions }} câu
                  ({{ (item.correct_rate * 100).toFixed(1) }}%)
                </p>
              </div>
              <span :class="['w-fit px-3 py-1 rounded-full text-sm font-bold', item.total_score >= 8 ? 'bg-green-100 text-green-700' : item.total_score >= 5 ? 'bg-blue-100 text-blue-700' : 'bg-red-100 text-red-700']">
                {{ item.total_score.toFixed(1) }} điểm
              </span>
            </div>

            <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <div>
                <p class="mb-2 text-sm font-semibold text-gray-700">Theo chủ đề</p>
                <div class="space-y-2">
                  <div
                    v-for="bucket in item.by_topic"
                    :key="bucket.key"
                    class="rounded border border-gray-200 bg-gray-50 px-3 py-2"
                  >
                    <div class="flex justify-between gap-3 text-sm">
                      <span class="font-medium text-gray-700">{{ bucket.label }}</span>
                      <span class="font-semibold">{{ bucket.correct }}/{{ bucket.total }}</span>
                    </div>
                    <div class="mt-2 h-1.5 rounded-full bg-gray-200">
                      <div
                        class="h-1.5 rounded-full bg-blue-500"
                        :style="{ width: `${Math.round(bucket.correct_rate * 100)}%` }"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <p class="mb-2 text-sm font-semibold text-gray-700">Theo mức độ</p>
                <div class="space-y-2">
                  <div
                    v-for="bucket in item.by_difficulty"
                    :key="bucket.key"
                    class="flex items-center justify-between gap-3 rounded border border-gray-200 px-3 py-2 text-sm"
                  >
                    <span class="font-medium text-gray-700">{{ difficultyLabel(bucket.key) }}</span>
                    <span class="font-semibold">
                      {{ bucket.correct }}/{{ bucket.total }}
                      <span class="text-xs text-gray-500">({{ (bucket.correct_rate * 100).toFixed(1) }}%)</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="studentResults.length > 0" class="bg-white rounded shadow overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-50 border-b">
            <tr>
              <th class="p-4 text-left">Bài thi</th>
              <th class="p-4 text-left">Điểm</th>
              <th class="p-4 text-left">Ngày nộp</th>
              <th class="p-4 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in studentResults" :key="r.id" class="border-b hover:bg-gray-50">
              <td class="p-4 flex items-center gap-2">
                <CheckCircle class="w-4 h-4 text-green-500" />
                {{ examTitle(r.exam_id) }}
              </td>
              <td class="p-4">
                <span :class="['px-3 py-1 rounded-full text-sm font-bold', r.total_score >= 8 ? 'bg-green-100 text-green-700' : r.total_score >= 5 ? 'bg-blue-100 text-blue-700' : 'bg-red-100 text-red-700']">
                  {{ r.total_score.toFixed(1) }}
                </span>
              </td>
              <td class="p-4">{{ formatDate(r.finished_at) }}</td>
              <td class="p-4 text-right">
                <button
                  v-if="canViewAnswers(r.exam_id)"
                  @click="loadReview(r.id)"
                  :disabled="loadingReview"
                  class="text-blue-600 text-sm inline-flex items-center gap-1 justify-end w-full disabled:opacity-50"
                >
                  <Eye class="w-4 h-4" />
                  Xem bài
                </button>
                <span v-else class="text-gray-400 text-sm inline-flex items-center gap-1 justify-end w-full">
                  <EyeOff class="w-4 h-4" />
                  Chưa mở
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div
      v-if="showReviewModal && selectedReview"
      class="modal-overlay z-100 items-start pt-16 sm:pt-20 overflow-y-auto"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[88vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="font-bold text-lg">{{ selectedReview.exam_title }}</h3>
            <p class="text-sm text-gray-500">
              Điểm: {{ selectedReview.total_score.toFixed(1) }} | Nộp bài: {{ formatDate(selectedReview.finished_at) }}
            </p>
          </div>
          <button @click="showReviewModal = false" class="p-1 rounded hover:bg-gray-100">
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
              <span class="font-semibold">Câu {{ idx + 1 }}:</span>
              <p class="flex-1">{{ q.content }}</p>
              <span
                :class="['text-xs px-2 py-1 rounded-full inline-flex items-center gap-1', q.is_correct ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']"
              >
                <CircleCheck v-if="q.is_correct" class="w-3 h-3" />
                <CircleX v-else class="w-3 h-3" />
                {{ q.is_correct ? 'Đúng' : 'Sai' }}
              </span>
            </div>

            <div class="space-y-2">
              <div
                v-for="([key, value], optIdx) in optionEntries(q.options)"
                :key="key"
                :class="[
                  'p-3 rounded border text-sm',
                  hasAnswerKey(q.correct_answer, key)
                    ? 'bg-green-50 border-green-200'
                    : hasAnswerKey(q.student_answer, key)
                      ? 'bg-red-50 border-red-200'
                      : 'bg-gray-50 border-gray-200'
                ]"
              >
                <span class="font-semibold mr-2">{{ String.fromCharCode(65 + optIdx) }}.</span>
                <span>{{ value }}</span>
                <span v-if="hasAnswerKey(q.correct_answer, key)" class="ml-2 text-green-700 font-medium">(Đáp án đúng)</span>
                <span v-if="hasAnswerKey(q.student_answer, key) && !hasAnswerKey(q.correct_answer, key)" class="ml-2 text-red-700 font-medium">(Bạn chọn)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
