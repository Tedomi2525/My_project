import type { Class, AvailableStudent } from '~/types'

export const useClasses = (userId: Ref<number | undefined>) => {
  const config = useRuntimeConfig()

  const classes = ref<Class[]>([])
  const loading = ref(false)

  const authHeader = () => {
    if (!userId.value) {
      throw new Error('User ID chưa sẵn sàng')
    }
    return {
      'x-user-id': String(userId.value)
    }
  }

  /* ================= GET ================= */
  const getClasses = async (): Promise<Class[]> => {
    if (!userId.value) return []

    loading.value = true
    try {
      const res = await $fetch<Class[]>('/classes', {
        baseURL: config.public.apiBase,
        headers: authHeader()
      })
      classes.value = res
      return res
    } finally {
      loading.value = false
    }
  }

  const getClassDetail = async (id: number): Promise<Class> => {
    const res: any = await $fetch(`/classes/${id}`, {
      baseURL: config.public.apiBase,
      headers: authHeader()
    })

    return {
      id: res.id,
      name: res.name,
      description: res.description,
      teacher_id: res.teacher_id,
      students: res.students.map((s: any) => ({
        id: s.id,
        full_name: s.full_name,
        email: s.email,
        student_code: s.student_code,
        joined_at: s.joined_at
      }))
    }
  }

  const createClass = async (payload: { name: string; description?: string }) => {
    await $fetch('/classes', {
      method: 'POST',
      body: payload,
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
    await getClasses()
  }

  const updateClass = async (id: number, payload: any) => {
    await $fetch(`/classes/${id}`, {
      method: 'PUT',
      body: payload,
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
    await getClasses()
  }

  const deleteClass = async (id: number) => {
    await $fetch(`/classes/${id}`, {
      method: 'DELETE',
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
    await getClasses()
  }

  const removeStudent = async (classId: number, studentId: number) => {
    await $fetch(`/classes/${classId}/students/${studentId}`, {
      method: 'DELETE',
      baseURL: config.public.apiBase,
      headers: authHeader()
    })
    return getClassDetail(classId)
  }
  const getAvailableStudents = (classId: number) =>
    $fetch<AvailableStudent[]>(`/classes/${classId}/available-students`, {
      baseURL: config.public.apiBase,
      headers: authHeader()
    })

const addStudent = async (classId: number, studentId: number) => {
  await $fetch(`/classes/${classId}/students/${studentId}`, {
    method: 'POST',
    baseURL: config.public.apiBase,
    headers: authHeader()
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
    removeStudent,
    getAvailableStudents,
    addStudent
  }

}
