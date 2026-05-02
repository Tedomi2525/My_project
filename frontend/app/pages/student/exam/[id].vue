<script setup lang="ts">
import { Clock, AlertCircle, CheckCircle, ArrowLeft, ArrowRight, Flag } from 'lucide-vue-next'
import type { Question, Exam } from '~/types'
import { useExams } from '~/composables/useExams'
import { useAuth } from '~/composables/useAuth'

definePageMeta({ layout: 'student' })
const route = useRoute()
const router = useRouter()
const examId = Number(route.params.id)
const { user } = useAuth()

const {
  getExamById,
  getExamQuestions,
  submitExam,
  startExam: startExamSession,
  autosaveExam,
  logExamViolation
} = useExams()

const mockExam = ref<Exam | null>(null)
const mockQuestions = ref<Question[]>([])
const pending = ref(true)

const started = ref(false)
const submitted = ref(false)
const currentQuestion = ref(0)
const answers = ref<string[]>([])
const flaggedQuestions = ref<boolean[]>([])
const timeLeft = ref(0)
const showConfirmModal = ref(false)
const score = ref(0)
const reviewQuestions = ref<Array<{
  question_id: number
  content: string
  options: Record<string, string> | null
  correct_answer: string
  student_answer: string
  is_correct: boolean
}>>([])
const violationCount = ref(0)
const maxViolations = 3
const antiCheatNotice = ref('')
const antiCheatWarningVisible = ref(false)

let timer: ReturnType<typeof setInterval> | null = null
let warningTimer: ReturnType<typeof setTimeout> | null = null
let autosaveTimer: ReturnType<typeof setInterval> | null = null

const answersByQuestionId = () => {
  return mockQuestions.value.reduce<Record<string, string>>((acc, question, index) => {
    const answer = answers.value[index]
    if (answer) acc[String(question.id)] = answer
    return acc
  }, {})
}

const restoreAnswers = (savedAnswers: Record<string, string> | undefined) => {
  if (!savedAnswers) return
  mockQuestions.value.forEach((question, index) => {
    const saved = savedAnswers[String(question.id)]
    if (saved) answers.value[index] = saved
  })
}

const saveProgress = async () => {
  if (!isExamInProgress.value) return
  try {
    await autosaveExam(examId, answersByQuestionId())
  } catch (error) {
    console.error('Khong the tu dong luu bai lam:', error)
  }
}

const questionData = computed(() => {
  if (mockQuestions.value.length === 0) return undefined
  return mockQuestions.value[currentQuestion.value]
})

const getOptionEntries = (options: Question['options']): Array<[string, string]> => {
  if (!options || Array.isArray(options)) return []
  return Object.entries(options).map(([key, value]) => [key, String(value)])
}

const shuffleArray = <T>(arr: T[]): T[] => {
  const cloned = [...arr]
  for (let i = cloned.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[cloned[i], cloned[j]] = [cloned[j], cloned[i]]
  }
  return cloned
}

const shuffleQuestionOptions = (question: Question): Question => {
  const entries = getOptionEntries(question.options)
  if (entries.length <= 1) return question

  const shuffledEntries = shuffleArray(entries)
  const shuffledOptions = shuffledEntries.reduce<Record<string, string>>((acc, [key, text]) => {
    acc[key] = text
    return acc
  }, {})

  return {
    ...question,
    options: shuffledOptions
  }
}

const currentOptionEntries = computed(() => getOptionEntries(questionData.value?.options ?? null))
const isExamInProgress = computed(() => started.value && !submitted.value)
const flaggedCount = computed(() => flaggedQuestions.value.filter(Boolean).length)
const isCurrentQuestionFlagged = computed(() => Boolean(flaggedQuestions.value[currentQuestion.value]))

const showWarning = (message: string) => {
  antiCheatNotice.value = message
  antiCheatWarningVisible.value = true
  if (warningTimer) clearTimeout(warningTimer)
  warningTimer = setTimeout(() => {
    antiCheatWarningVisible.value = false
  }, 4000)
}

const registerViolation = async (reason: string) => {
  if (!isExamInProgress.value) return

  violationCount.value += 1
  try {
    await logExamViolation(examId, reason)
  } catch (error) {
    console.error('Khong the ghi log vi pham:', error)
  }
  showWarning(`${reason} (Vi phạm ${violationCount.value}/${maxViolations})`)

  if (violationCount.value >= maxViolations) {
    showWarning('Vượt quá giới hạn vi phạm. Hệ thống sẽ tự động nộp bài.')
    await handleSubmit()
  }
}

const enterFullscreen = async () => {
  if (!document.fullscreenEnabled || document.fullscreenElement) return
  try {
    await document.documentElement.requestFullscreen()
  } catch (error) {
    await registerViolation('Không thể bật toàn màn hình')
  }
}

const exitFullscreen = async () => {
  if (!document.fullscreenElement) return
  try {
    await document.exitFullscreen()
  } catch (error) {
    // no-op
  }
}

const handleVisibilityChange = async () => {
  if (document.hidden) await registerViolation('Phát hiện rời khỏi tab bài thi')
}

const handleWindowBlur = async () => {
  await registerViolation('Phát hiện chuyển sang cửa sổ khác')
}

const handleFullscreenChange = async () => {
  if (!isExamInProgress.value) return
  if (!document.fullscreenElement) await registerViolation('Phát hiện thoát toàn màn hình')
}

const handleKeydown = async (event: KeyboardEvent) => {
  if (!isExamInProgress.value) return

  const key = event.key.toLowerCase()
  const blockedCombo = (event.ctrlKey || event.metaKey) && ['c', 'v', 'x', 'p', 's', 'u'].includes(key)

  if (blockedCombo || event.key === 'PrintScreen') {
    event.preventDefault()
    await registerViolation('Phát hiện thao tác bị cấm')
  }
}

const preventClipboardActions = (event: Event) => {
  if (!isExamInProgress.value) return
  event.preventDefault()
}

const handleBeforeUnload = (event: BeforeUnloadEvent) => {
  if (!isExamInProgress.value) return
  event.preventDefault()
  event.returnValue = ''
}

onMounted(async () => {
  document.addEventListener('visibilitychange', handleVisibilityChange)
  window.addEventListener('blur', handleWindowBlur)
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  window.addEventListener('keydown', handleKeydown, true)
  document.addEventListener('copy', preventClipboardActions)
  document.addEventListener('cut', preventClipboardActions)
  document.addEventListener('paste', preventClipboardActions)
  document.addEventListener('contextmenu', preventClipboardActions)
  window.addEventListener('beforeunload', handleBeforeUnload)

  try {
    const [examRes, questionsRes] = await Promise.all([
      getExamById(examId),
      getExamQuestions(examId)
    ])

    mockExam.value = examRes

    let preparedQuestions = [...questionsRes]
    if (mockExam.value?.shuffle_options) {
      preparedQuestions = preparedQuestions.map((q) => shuffleQuestionOptions(q))
    }
    if (mockExam.value?.shuffle_questions) {
      preparedQuestions = shuffleArray(preparedQuestions)
    }
    mockQuestions.value = preparedQuestions

    if (mockExam.value?.duration_minutes) {
      timeLeft.value = mockExam.value.duration_minutes * 60
    }

    if (mockQuestions.value.length > 0) {
      answers.value = new Array(mockQuestions.value.length).fill('')
      flaggedQuestions.value = new Array(mockQuestions.value.length).fill(false)
    }
  } catch (error) {
    console.error('Lỗi khi tải dữ liệu bài thi:', error)
  } finally {
    pending.value = false
  }
})

watch(started, (newValue) => {
  if (newValue && !submitted.value) {
    timer = setInterval(() => {
      if (timeLeft.value <= 1) {
        handleSubmit()
        if (timer) clearInterval(timer)
        timeLeft.value = 0
      } else {
        timeLeft.value--
      }
    }, 1000)
    autosaveTimer = setInterval(saveProgress, 15000)
  }
})

watch(submitted, async (newValue) => {
  if (newValue) {
    if (autosaveTimer) clearInterval(autosaveTimer)
    await exitFullscreen()
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (warningTimer) clearTimeout(warningTimer)
  if (autosaveTimer) clearInterval(autosaveTimer)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  window.removeEventListener('blur', handleWindowBlur)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  window.removeEventListener('keydown', handleKeydown, true)
  document.removeEventListener('copy', preventClipboardActions)
  document.removeEventListener('cut', preventClipboardActions)
  document.removeEventListener('paste', preventClipboardActions)
  document.removeEventListener('contextmenu', preventClipboardActions)
  window.removeEventListener('beforeunload', handleBeforeUnload)
})

const handleAnswerSelect = (optionKey: string) => {
  answers.value[currentQuestion.value] = optionKey
  saveProgress()
}

const toggleFlagCurrentQuestion = () => {
  flaggedQuestions.value[currentQuestion.value] = !flaggedQuestions.value[currentQuestion.value]
}

const getQuestionNavClass = (index: number) => {
  if (currentQuestion.value === index) return 'bg-blue-600 text-white ring-2 ring-blue-300'
  if (flaggedQuestions.value[index]) return 'bg-amber-100 text-amber-700 hover:bg-amber-200'
  if (answers.value[index]) return 'bg-green-100 text-green-700'
  return 'bg-gray-100 text-gray-600 hover:bg-gray-200'
}

const handleSubmit = async () => {
  if (submitted.value) return

  if (timer) clearInterval(timer)
  if (autosaveTimer) clearInterval(autosaveTimer)

  try {
    const payload = mockQuestions.value
      .map((q, idx) => {
        const selected = answers.value[idx]
        if (!selected) return null
        return {
          question_id: q.id,
          student_answer: selected
        }
      })
      .filter((item): item is { question_id: number; student_answer: string } => item !== null)

    const examPassword = mockExam.value?.has_password
      ? sessionStorage.getItem(`exam-password:${examId}`) || ''
      : undefined
    const result: any = await submitExam(examId, payload, examPassword)

    score.value = Number(result?.total_score ?? 0)

    if (mockExam.value?.allow_view_answers && result?.id) {
      try {
        const tokenCookie = useCookie<string | null>('token')
        const config = useRuntimeConfig()
        const review: any = await $fetch(`/results/${result.id}/review`, {
          baseURL: config.public.apiBase,
          headers: {
            Authorization: `Bearer ${tokenCookie.value || ''}`,
            'x-user-id': String(user.value?.id || ''),
            'x-user-role': String(user.value?.role || '')
          }
        })
        reviewQuestions.value = review?.questions || []
      } catch (reviewError) {
        reviewQuestions.value = []
      }
    }

    submitted.value = true
    showConfirmModal.value = false
  } catch (error) {
    console.error('Lỗi khi nộp bài:', error)
    const err = error as any
    const detail =
      err?.data?.detail ||
      err?.response?._data?.detail ||
      err?.message ||
      ''

    if (typeof detail === 'string' && detail.toLowerCase().includes('attempt limit reached')) {
      alert('Bạn đã hết số lần làm bài cho đề thi này.')
    } else {
      alert('Có lỗi xảy ra khi nộp bài, vui lòng thử lại!')
    }
  }
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const nextQuestion = () => {
  if (currentQuestion.value < mockQuestions.value.length - 1) currentQuestion.value++
}

const prevQuestion = () => {
  if (currentQuestion.value > 0) currentQuestion.value--
}

const startExam = async () => {
  try {
    const session = await startExamSession(examId)
    violationCount.value = Number(session.violation_count || 0)
    restoreAnswers(session.answers)
    started.value = true
  } catch (error: any) {
    alert(error?.data?.detail || error?.message || 'Khong the bat dau bai thi')
    return
  }
  await nextTick()
  await enterFullscreen()
}
</script>

<template>
  <div v-if="pending" class="max-w-4xl mx-auto text-center py-20 flex flex-col items-center justify-center">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
    <p class="text-gray-600 font-medium text-lg">Đang tải dữ liệu bài thi...</p>
  </div>

  <div v-else-if="!mockExam" class="max-w-4xl mx-auto text-center py-8">
    <div class="panel-card p-8">
      <h2 class="text-xl font-bold mb-4">Không tìm thấy bài thi</h2>
      <button @click="router.push('/student')" class="bg-blue-600 text-white px-6 py-2 rounded-lg">Quay lai</button>
    </div>
  </div>

  <div v-else-if="!started && !submitted" class="max-w-4xl mx-auto">
    <div class="panel-card p-8">
      <div class="text-center mb-8">
        <div class="inline-block p-4 bg-blue-100 rounded-full mb-4">
          <CheckCircle class="w-12 h-12 text-blue-600" />
        </div>
        <h1 class="mb-2 text-2xl font-bold">{{ mockExam.title }}</h1>
        <p class="text-gray-600">Vui lòng đọc kỹ hướng dẫn trước khi bắt đầu làm bài</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div class="bg-blue-50 rounded-lg p-4 text-center">
          <p class="text-gray-600">Số câu hỏi</p>
          <p class="text-3xl text-blue-600 font-bold">{{ mockQuestions.length }}</p>
        </div>
        <div class="bg-green-50 rounded-lg p-4 text-center">
          <p class="text-gray-600">Thời gian</p>
          <p class="text-3xl text-green-600 font-bold">{{ mockExam.duration_minutes }} phút</p>
        </div>
        <div class="bg-purple-50 rounded-lg p-4 text-center">
          <p class="text-gray-600">Điểm tối đa</p>
          <p class="text-3xl text-purple-600 font-bold">10</p>
        </div>
      </div>

      <div class="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-amber-800 text-sm">
        <p class="font-semibold mb-2">Quy định chống gian lận</p>
        <ul class="list-disc pl-5 space-y-1">
          <li>Bắt buộc làm bài ở chế độ toàn màn hình.</li>
          <li>Rời tab, thoát toàn màn hình hoặc dùng phím tắt bị cấm sẽ bị tính vi phạm.</li>
          <li>Vi phạm từ 3 lần trở lên sẽ tự động nộp bài.</li>
          <li>Trình duyệt không thể chặn chụp màn hình 100%, hệ thống chỉ phát hiện được một số hành vi.</li>
        </ul>
      </div>

      <button @click="startExam" class="w-full px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-lg font-bold">
        Bắt đầu làm bài
      </button>
    </div>
  </div>

  <div v-else-if="submitted" class="max-w-4xl mx-auto">
    <div class="panel-card mb-6 p-8 text-center">
      <h2 class="mb-4 font-bold text-2xl">Đã nộp bài thành công!</h2>
      <div class="text-6xl mb-4">{{ score >= 8 ? 'Tốt' : score >= 5 ? 'Khá' : 'Cần cố gắng hơn' }}</div>
      <p class="text-gray-600 mb-2">Điểm số của bạn</p>
      <p :class="['text-6xl mb-6 font-bold', score >= 8 ? 'text-green-600' : score >= 5 ? 'text-blue-600' : 'text-orange-600']">{{ score.toFixed(1) }}</p>
      <button @click="router.push('/student/history')" class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">Xem lịch sử thi</button>
    </div>

    <div v-if="mockExam.allow_view_answers" class="panel-card p-8">
      <h3 class="mb-6 font-bold text-xl">Đáp án chi tiết</h3>
      <div class="space-y-6">
        <div v-for="(q, idx) in reviewQuestions" :key="q.question_id" class="border-b pb-6">
          <div class="flex items-start gap-3 mb-4">
            <span :class="['px-3 py-1 rounded-full text-sm font-bold', q.is_correct ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">Câu {{ idx + 1 }}</span>
            <p class="flex-1 font-medium">{{ q.content }}</p>
          </div>
          <div class="ml-16 space-y-2">
            <div
              v-for="[key, opt] in getOptionEntries(q.options)"
              :key="key"
              :class="['p-3 rounded-lg flex border', key === q.correct_answer ? 'bg-green-50 border-green-200' : q.student_answer === key && key !== q.correct_answer ? 'bg-red-50 border-red-200' : 'bg-gray-50 border-transparent']"
            >
              <span class="mr-2 font-bold">{{ key }}.</span>
              <span class="flex-1">{{ opt }}</span>
              <span v-if="key === q.correct_answer" class="text-green-600 ml-2 font-medium">(Đáp án đúng)</span>
              <span v-if="q.student_answer === key && key !== q.correct_answer" class="text-red-600 ml-2 font-medium">(Bạn chọn)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="flex flex-col lg:flex-row gap-6">
    <div
      v-if="antiCheatWarningVisible"
      class="fixed right-4 top-24 z-[70] max-w-sm rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 shadow-lg"
    >
      <p class="font-semibold mb-1"> Cảnh báo gian lận</p>
      <p class="text-sm">{{ antiCheatNotice }}</p>
    </div>

    <div class="w-full lg:w-64 shrink-0 order-2 lg:order-1">
      <div class="panel-card sticky top-6">
        <div :class="['flex items-center gap-2 px-4 py-3 rounded-lg mb-4 font-bold text-xl', timeLeft < 300 ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700']">
          <Clock class="w-5 h-5" /> {{ formatTime(timeLeft) }}
        </div>
        <div class="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          Vi phạm: <strong>{{ violationCount }}/{{ maxViolations }}</strong>
        </div>
        <h3 class="mb-4 font-bold">Danh sách câu hỏi</h3>
        <div class="grid grid-cols-4 gap-2 mb-6">
          <button
            v-for="(_, i) in mockQuestions"
            :key="i"
            @click="currentQuestion = i"
            :class="['relative aspect-square rounded-lg flex items-center justify-center font-medium transition-colors', getQuestionNavClass(i)]"
          >
            {{ i + 1 }}
            <Flag v-if="flaggedQuestions[i]" class="absolute top-1 right-1 w-3.5 h-3.5" />
          </button>
        </div>
        <p class="mb-6 text-xs text-gray-500">Màu vàng là câu đang đánh dấu phân vân.</p>
        <button @click="showConfirmModal = true" class="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 font-bold transition-colors">Nộp bài</button>
      </div>
    </div>

    <div class="flex-1 order-1 lg:order-2">
      <div v-if="timeLeft < 300" class="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6 flex gap-3 text-orange-700 animate-pulse">
        <AlertCircle class="w-5 h-5" /> Sắp hết thời gian!
      </div>

      <div v-if="questionData" class="panel-card mb-6 p-8">
        <div class="flex items-start gap-4 mb-6">
          <span class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg font-bold whitespace-nowrap">Câu {{ currentQuestion + 1 }}/{{ mockQuestions.length }}</span>
          <h2 class="flex-1 text-lg font-medium">{{ questionData.content }}</h2>
          <button
            type="button"
            @click="toggleFlagCurrentQuestion"
            :class="[
              'inline-flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors',
              isCurrentQuestionFlagged
                ? 'border-amber-300 bg-amber-100 text-amber-700 hover:bg-amber-200'
                : 'border-gray-300 bg-white text-gray-600 hover:bg-gray-50'
            ]"
          >
            <Flag class="w-4 h-4" />
            {{ isCurrentQuestionFlagged ? 'Bỏ đánh dấu' : 'Đánh dấu' }}
          </button>
        </div>

        <div class="space-y-3">
          <label
            v-for="[key, opt] in currentOptionEntries"
            :key="key"
            :class="['flex items-start gap-4 p-5 rounded-lg cursor-pointer transition-all border-2', answers[currentQuestion] === key ? 'bg-blue-50 border-blue-500 shadow-md' : 'bg-gray-50 border-transparent hover:bg-gray-100']"
          >
            <input
              type="radio"
              :name="`q-${currentQuestion}`"
              :checked="answers[currentQuestion] === key"
              @change="handleAnswerSelect(key)"
              class="mt-1.5 w-5 h-5 accent-blue-600"
            />
            <div class="flex-1">
              <span class="font-bold mr-3">{{ key }}.</span>
              <span>{{ opt }}</span>
            </div>
          </label>
        </div>
      </div>

      <div class="flex justify-between">
        <button @click="prevQuestion" :disabled="currentQuestion === 0" class="flex gap-2 items-center px-6 py-3 rounded-lg bg-white shadow disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors">
          <ArrowLeft class="w-5 h-5" /> Câu trước
        </button>
        <button @click="nextQuestion" :disabled="currentQuestion === mockQuestions.length - 1" class="flex gap-2 items-center px-6 py-3 rounded-lg bg-white shadow disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors">
          Câu sau <ArrowRight class="w-5 h-5" />
        </button>
      </div>
    </div>

    <div v-if="showConfirmModal" class="modal-overlay">
      <div class="modal-card w-full max-w-md p-8">
        <h2 class="mb-4 font-bold text-xl">Xác nhận nộp bài</h2>
        <div class="mb-6">
          <p>Bạn đã trả lời <strong>{{ answers.filter((a) => !!a).length }}/{{ mockQuestions.length }}</strong> câu hỏi.</p>
          <div v-if="answers.some((a) => !a)" class="mt-2 bg-orange-50 border border-orange-200 p-3 rounded text-orange-700 flex gap-2">
            <AlertCircle class="w-5 h-5 shrink-0" />
            <span>Còn <strong>{{ answers.filter((a) => !a).length }}</strong> câu chưa làm.</span>
          </div>
          <div v-if="flaggedCount > 0" class="mt-2 bg-amber-50 border border-amber-200 p-3 rounded text-amber-700 flex gap-2">
            <Flag class="w-5 h-5 shrink-0" />
            <span>Bạn đang đánh dấu <strong>{{ flaggedCount }}</strong> câu cần xem lại.</span>
          </div>
        </div>
        <div class="flex gap-3">
          <button @click="showConfirmModal = false" class="btn-secondary flex-1">Làm tiếp</button>
          <button @click="handleSubmit" class="flex-1 py-3 bg-green-600 text-white rounded-lg font-bold hover:bg-green-700 shadow-lg">Nộp bài</button>
        </div>
      </div>
    </div>
  </div>
</template>
