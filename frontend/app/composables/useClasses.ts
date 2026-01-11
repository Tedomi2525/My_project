import type { Class } from '~/types'
import { useAuth } from '~/composables/useAuth'

export const useClasses = () => {
  const { user } = useAuth()
  const config = useRuntimeConfig()

  const classes = ref<Class[]>([])
  const loading = ref(false)

  /* ================= GET CLASSES ================= */
  const getClasses = async (): Promise<Class[]> => {
    if (!user.value?.id) {
      console.warn('❌ Chưa có user.id')
      return []
    }

    loading.value = true
    try {
      const res = await $fetch<Class[]>('/classes', {
        baseURL: config.public.apiBase,
        headers: {
          'x-user-id': String(user.value.id)
        }
      })

      classes.value = res
      return res
    } finally {
      loading.value = false
    }
  }

  /* ================= GET CLASS DETAIL ================= */
  const getClassDetail = (id: number) =>
    $fetch<Class>(`/classes/${id}`, {
      baseURL: config.public.apiBase,
      headers: {
        'x-user-id': String(user.value?.id)
      }
    })

  /* ================= CREATE ================= */
  const createClass = async (payload: {
    name: string
    description?: string
  }) => {
    await $fetch('/classes', {
      method: 'POST',
      body: payload,
      baseURL: config.public.apiBase,
      headers: {
        'x-user-id': String(user.value?.id)
      }
    })
    await getClasses()
  }

  /* ================= UPDATE ================= */
  const updateClass = async (id: number, payload: any) => {
    await $fetch(`/classes/${id}`, {
      method: 'PUT',
      body: payload,
      baseURL: config.public.apiBase,
      headers: {
        'x-user-id': String(user.value?.id)
      }
    })
    await getClasses()
  }

  /* ================= DELETE ================= */
  const deleteClass = async (id: number) => {
    await $fetch(`/classes/${id}`, {
      method: 'DELETE',
      baseURL: config.public.apiBase,
      headers: {
        'x-user-id': String(user.value?.id)
      }
    })
    await getClasses()
  }

  /* ================= REMOVE STUDENT ================= */
  const removeStudent = async (classId: number, studentId: number) => {
    await $fetch(`/classes/${classId}/students/${studentId}`, {
      method: 'DELETE',
      baseURL: config.public.apiBase,
      headers: {
        'x-user-id': String(user.value?.id)
      }
    })

    return getClassDetail(classId)
  }

  return {
    classes,
    loading,
    getClasses,
    getClassDetail,
    createClass,
    updateClass,
    deleteClass,
    removeStudent
  }
}
