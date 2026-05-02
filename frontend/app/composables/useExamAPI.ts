// composites/useExamApi.ts
import type { Exam } from '~/types'

export const useExamApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase
  const tokenCookie = useCookie<string | null>('token')

  return {
    getAvailableExams: () =>
      useFetch<Exam[]>('/exams/student-available', { baseURL: apiBase }),

    verifyPassword: (examId: string, password: string, userId: number, userRole: string) =>
      $fetch<{ success: boolean }>(`/exams/${examId}/check-password`, {
        method: 'POST',
        baseURL: apiBase,
        headers: {
          Authorization: `Bearer ${tokenCookie.value || ''}`
        },
        body: { password }
      })
  }
}
