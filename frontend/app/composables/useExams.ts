// ~/composables/useExams.ts
import type { Exam } from '~/types'

export const useExams = () => {
  const { $api } = useNuxtApp()

  const exams = ref<Exam[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  /* ================= GET ================= */

  const getExams = async () => {
    loading.value = true
    try {
      const res = await $api.get<Exam[]>('/exams')
      exams.value = res.data
      return res
    } catch (err: any) {
      error.value = err?.data?.detail || 'Không lấy được danh sách đề thi'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getExamById = async (examId: number) => {
    try {
      return await $api.get<Exam>(`/exams/${examId}`)
    } catch (err) {
      throw err
    }
  }

  /* ================= CREATE ================= */

  const createExam = async (payload: {
    title: string
    description?: string
    duration_minutes: number
    start_time?: string
    end_time?: string
    created_by: number
    password?: string
    show_answers?: boolean // [Cập nhật]
    class_ids?: number[]   // [Cập nhật] Thêm danh sách lớp
  }) => {
    try {
      return await $api.post<Exam>('/exams', payload)
    } catch (err) {
      throw err
    }
  }

  /* ================= UPDATE ================= */

  const updateExam = async (
    examId: number,
    payload: Partial<{
      title: string
      description: string
      duration_minutes: number
      start_time: string
      end_time: string
      password: string | null
      show_answers: boolean // [Cập nhật]
      class_ids: number[]   // [Cập nhật] Thêm danh sách lớp
    }>
  ) => {
    try {
      return await $api.put<Exam>(`/exams/${examId}`, payload)
    } catch (err) {
      throw err
    }
  }

  /* ================= DELETE ================= */

  const deleteExam = async (examId: number) => {
    try {
      await $api.delete(`/exams/${examId}`)
      exams.value = exams.value.filter(e => e.id !== examId)
    } catch (err) {
      throw err
    }
  }

  /* ================= QUESTIONS ================= */

  const addQuestionToExam = async (payload: {
    exam_id: number
    question_id: number
    point?: number
  }) => {
    try {
      return await $api.post(
        `/exams/${payload.exam_id}/questions`,
        payload
      )
    } catch (err) {
      throw err
    }
  }

  const removeQuestionFromExam = async (
    examId: number,
    questionId: number
  ) => {
    try {
      await $api.delete(`/exams/${examId}/questions/${questionId}`)
    } catch (err) {
      throw err
    }
  }

  return {
    // state
    exams,
    loading,
    error,

    // methods
    getExams,
    getExamById,
    createExam,
    updateExam,
    deleteExam,
    addQuestionToExam,
    removeQuestionFromExam
  }
}