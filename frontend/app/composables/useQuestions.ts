// ~/composables/useQuestions.ts
import type { Question } from '~/types'

export const useQuestions = () => {
  const { $api } = useNuxtApp()

  const questions = ref<Question[]>([])
  const loading = ref(false)

  const getQuestions = async () => {
    loading.value = true
    try {
      const res = await $api.get<Question[]>('/questions')
      questions.value = res.data
    } finally {
      loading.value = false
    }
  }

  const createQuestion = async (data: any) => {
    await $api.post('/questions', data)
    await getQuestions()
  }

  const updateQuestion = async (id: number, data: any) => {
    await $api.put(`/questions/${id}`, data)
    await getQuestions()
  }

  const deleteQuestion = async (id: number) => {
    await $api.delete(`/questions/${id}`)
    await getQuestions()
  }

  return {
    questions,
    loading,
    getQuestions,
    createQuestion,
    updateQuestion,
    deleteQuestion
  }
}
