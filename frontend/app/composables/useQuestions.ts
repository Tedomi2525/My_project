// ~/composables/useQuestions.ts
import type { Question } from '~/types'

export const useQuestions = () => {
  const config = useRuntimeConfig()

  const questions = ref<Question[]>([])
  const loading = ref(false)

  const getQuestions = async () => {
    loading.value = true
    try {
      questions.value = await $fetch<Question[]>('/questions', {
        baseURL: config.public.apiBase
      })
    } finally {
      loading.value = false
    }
  }

  const createQuestion = async (data: any) => {
    await $fetch('/questions', {
      method: 'POST',
      baseURL: config.public.apiBase,
      body: data
    })
    await getQuestions()
  }

  const updateQuestion = async (id: number, data: any) => {
    await $fetch(`/questions/${id}`, {
      method: 'PUT',
      baseURL: config.public.apiBase,
      body: data
    })
    await getQuestions()
  }

  const deleteQuestion = async (id: number) => {
    await $fetch(`/questions/${id}`, {
      method: 'DELETE',
      baseURL: config.public.apiBase
    })
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
