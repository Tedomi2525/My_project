// composites/useExamApi.ts
import type { Exam } from '~/types'

export const useExamApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  return {
    getAvailableExams: () =>
      useFetch<Exam[]>('/exams/student-available', { baseURL: apiBase }),

    verifyPassword: (examId: string, password: string, userId: number, userRole: string) =>
      $fetch<{ success: boolean }>(`/exams/${examId}/check-password`, {
        method: 'POST',
        baseURL: apiBase,
        headers: {
          'x-user-id': String(userId),
          'x-user-role': String(userRole)
        },
        body: { password }
      })
  }
}
