import type { Exam, Question } from '~/types'
import { useAuth } from '~/composables/useAuth'

export const useExams = () => {
  const config = useRuntimeConfig()
  const { user, fetchUser } = useAuth()

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
    if (!user.value) {
      throw new Error('Chua dang nhap')
    }
    return {
      'x-user-id': String(user.value.id)
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
    answers: Array<{ question_id: number; student_answer: string }>
  ) => {
    await ensureAuth()

    const payload = answers.map((answer) => ({
      result_id: 0,
      question_id: answer.question_id,
      student_answer: answer.student_answer
    }))

    return await $fetch(`/results/submit/${examId}/${user.value.id}`, {
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

  return {
    exams,
    loading,
    getExams,
    getExamById,
    getExamQuestions,
    submitExam,
    createExam,
    updateExam,
    deleteExam
  }
}
