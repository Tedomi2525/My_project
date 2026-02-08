import type { Exam } from '~/types'
import { useAuth } from '~/composables/useAuth'

export const useExams = () => {
  const config = useRuntimeConfig()
  const { user } = useAuth()

  const exams = ref<Exam[]>([])
  const loading = ref(false)

  /* ================= HEADER ================= */

  const authHeader = () => {
    if (!user.value) {
      throw new Error('Chưa đăng nhập')
    }
    return {
      'x-user-id': String(user.value.id)
    }
  }

  /* ================= GET ================= */

  const getExams = async (): Promise<Exam[]> => {
    if (!user.value) return []

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
    return await $fetch<Exam>(`/exams/${id}`, {
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
  }

  /* ================= CREATE ================= */

  const createExam = async (payload: {
    title: string
    description?: string
    duration_minutes: number
    start_time?: string
    end_time?: string
    password?: string
    allow_view_answers?: boolean
    class_ids?: number[]
    questions?: number[]
  }) => {
    await $fetch('/exams', {
      method: 'POST',
      body: payload,
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
    await getExams()
  }

  /* ================= UPDATE ================= */

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
      class_ids: number[]
      questions: number[]
    }>
  ) => {
    await $fetch(`/exams/${id}`, {
      method: 'PUT',
      body: payload,
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
    await getExams()
  }

  /* ================= DELETE ================= */

  const deleteExam = async (id: number) => {
    await $fetch(`/exams/${id}`, {
      method: 'DELETE',
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
    await getExams()
  }

  /* ================= QUESTIONS ================= */

  const addQuestionToExam = async (examId: number, questionId: number) => {
    await $fetch(`/exams/${examId}/questions`, {
      method: 'POST',
      body: { question_id: questionId },
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
    return getExamById(examId)
  }

  const removeQuestionFromExam = async (examId: number, questionId: number) => {
    await $fetch(`/exams/${examId}/questions/${questionId}`, {
      method: 'DELETE',
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
    return getExamById(examId)
  }

  const getExamQuestions = async (examId: number) => {
    return await $fetch(`/exams/${examId}/questions`, {
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
  }

  return {
    exams,
    loading,
    getExams,
    getExamById,
    createExam,
    updateExam,
    deleteExam,
    addQuestionToExam,
    removeQuestionFromExam,
    getExamQuestions
  }
}
