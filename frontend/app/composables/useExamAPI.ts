// composites/useExamApi.ts
import type { Exam, ExamResult } from '~/types'

export const useExamApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase // Cấu hình trong nuxt.config.ts

  return {
    // Lấy danh sách bài thi cho sinh viên
    getAvailableExams: () => 
      useFetch<Exam[]>('/exams/student-available', { baseURL: apiBase }),

    // Kiểm tra mật khẩu bài thi qua backend
    verifyPassword: (examId: string, password: string, userId: number) => 
      $fetch<{ success: boolean }>(`/exams/${examId}/check-password`, {
        method: 'POST',
        baseURL: apiBase,
        headers: {
          'x-user-id': String(userId)
        },
        body: { password }
      })
  }
}
