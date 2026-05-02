import type { Exam, ExamSession, ExamViolation, Question } from '~/types'
import { useAuth } from '~/composables/useAuth'

export const useExams = () => {
  const config = useRuntimeConfig()
  const { user, fetchUser } = useAuth()
  const tokenCookie = useCookie<string | null>('token')

  const exams = ref<Exam[]>([])
  const loading = ref(false)

  const ensureAuth = async () => {
    if (!user.value) {
      await fetchUser()
    }
    if (!user.value) {
      throw new Error('Chua dang nhap')
    }
  }

  const authHeader = () => {
    if (!user.value || !tokenCookie.value) {
      throw new Error('Chua dang nhap')
    }
    return {
      Authorization: `Bearer ${tokenCookie.value}`,
      'x-user-id': String(user.value.id),
      'x-user-role': String(user.value.role)
    }
  }

  const getExams = async (): Promise<Exam[]> => {
    await ensureAuth()

    loading.value = true
    try {
      const res = await $fetch<Exam[]>('/exams', {
        baseURL: config.public.apiBase,
        headers: authHeader()
      })
      exams.value = res
      return res
    } finally {
      loading.value = false
    }
  }

  const getExamById = async (id: number): Promise<Exam> => {
    await ensureAuth()
    return await $fetch<Exam>(`/exams/${id}`, {
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
  }

  const getExamQuestions = async (id: number): Promise<Question[]> => {
    await ensureAuth()
    return await $fetch<Question[]>(`/exams/${id}/questions`, {
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
  }

  const submitExam = async (
    examId: number,
    answers: Array<{ question_id: number; student_answer: string }>,
    examPassword?: string
  ) => {
    await ensureAuth()

    const payload = {
      answers: answers.map((answer) => ({
        result_id: 0,
        question_id: answer.question_id,
        student_answer: answer.student_answer
      })),
      password: examPassword || undefined
    }

    return await $fetch(`/results/submit/${examId}`, {
      method: 'POST',
      body: payload,
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
  }

  const createExam = async (payload: {
    title: string
    description?: string
    duration_minutes: number
    start_time?: string
    end_time?: string
    password?: string
    allow_view_answers?: boolean
    max_attempts?: number | null
    shuffle_questions?: boolean
    shuffle_options?: boolean
    class_ids?: number[]
    questions: number[]
  }): Promise<Exam> => {
    await ensureAuth()
    const exam = await $fetch<Exam>('/exams', {
      method: 'POST',
      body: payload,
      baseURL: config.public.apiBase,
      headers: authHeader()
    })

    await getExams()
    return exam
  }

  const updateExam = async (
    id: number,
    payload: Partial<{
      title: string
      description: string
      duration_minutes: number
      start_time: string
      end_time: string
      password: string | null
      allow_view_answers: boolean
      max_attempts: number | null
      shuffle_questions: boolean
      shuffle_options: boolean
      status: 'draft' | 'published' | 'closed'
      class_ids: number[]
      questions: number[]
    }>
  ) => {
    await ensureAuth()
    await $fetch(`/exams/${id}`, {
      method: 'PUT',
      body: payload,
      baseURL: config.public.apiBase,
      headers: authHeader()
    })

    await getExams()
  }

  const deleteExam = async (id: number) => {
    await ensureAuth()
    await $fetch(`/exams/${id}`, {
      method: 'DELETE',
      baseURL: config.public.apiBase,
      headers: authHeader()
    })

    await getExams()
  }

  const updateExamStatus = async (id: number, status: 'draft' | 'published' | 'closed') => {
    await ensureAuth()
    const exam = await $fetch<Exam>(`/exams/${id}/status`, {
      method: 'PATCH',
      body: { status },
      baseURL: config.public.apiBase,
      headers: authHeader()
    })

    await getExams()
    return exam
  }

  const startExam = async (id: number): Promise<ExamSession> => {
    await ensureAuth()
    return await $fetch<ExamSession>(`/exams/${id}/start`, {
      method: 'POST',
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
  }

  const autosaveExam = async (id: number, answers: Record<string, string>): Promise<ExamSession> => {
    await ensureAuth()
    return await $fetch<ExamSession>(`/exams/${id}/autosave`, {
      method: 'PUT',
      body: { answers },
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
  }

  const logExamViolation = async (id: number, reason: string): Promise<ExamViolation> => {
    await ensureAuth()
    return await $fetch<ExamViolation>(`/exams/${id}/violations`, {
      method: 'POST',
      body: { reason },
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
  }

  return {
    exams,
    loading,
    getExams,
    getExamById,
    getExamQuestions,
    submitExam,
    createExam,
    updateExam,
    deleteExam,
    updateExamStatus,
    startExam,
    autosaveExam,
    logExamViolation
  }
}
