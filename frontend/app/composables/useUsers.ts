// ~/composables/useUsers.ts
import type { User } from '~/types'

export const useUsers = () => {
  const config = useRuntimeConfig()
  const API_BASE = config.public.apiBase

  const token = useCookie<string | null>('token')

  const api = <T>(url: string, options: any = {}) => {
    return $fetch<T>(url, {
      baseURL: API_BASE,
      headers: token.value
        ? { Authorization: `Bearer ${token.value}` }
        : {},
      ...options
    })
  }

  const getUsers = async (): Promise<User[]> => {
    try {
      const [admins, teachers, students] = await Promise.all([
        api<User[]>('/admins'),
        api<User[]>('/teachers'),
        api<User[]>('/students')
      ])
      return [...admins, ...teachers, ...students]
    } catch (error: any) {
      console.error('Lỗi lấy danh sách:', error)
      return []
    }
  }

  const createUser = async (payload: {
    username?: string
    password?: string
    fullName: string
    email?: string
    role: 'admin' | 'teacher' | 'student'
    studentId?: string
  }): Promise<User> => {
    try {
      const baseBody: Record<string, any> = {
        full_name: payload.fullName,
        email: payload.email
      }

      if (payload.role === 'admin') {
        return await api<User>('/admins', {
          method: 'POST',
          body: {
            ...baseBody,
            username: payload.username,
            password: payload.password
          }
        })
      }

      if (payload.role === 'teacher') {
        return await api<User>('/teachers', {
          method: 'POST',
          body: baseBody
        })
      }

      return await api<User>('/students', {
        method: 'POST',
        body: baseBody
      })
    } catch (error: any) {
      throw new Error(
        error?.data?.detail || 'Thêm mới thất bại'
      )
    }
  }

  const updateUser = async (
    id: number,
    role: 'admin' | 'teacher' | 'student',
    payload: Partial<Omit<User, 'id'>>
  ): Promise<User> => {
    try {
      const endpoint =
        role === 'admin'
          ? `/admins/${id}`
          : role === 'teacher'
            ? `/teachers/${id}`
            : `/students/${id}`

      return await api<User>(endpoint, {
        method: 'PUT',
        body: payload
      })
    } catch (error: any) {
      throw new Error(
        error?.data?.detail || 'Cập nhật thất bại'
      )
    }
  }

  const deleteUser = async (id: number, role: 'admin' | 'teacher' | 'student'): Promise<void> => {
    try {
      const endpoint =
        role === 'admin'
          ? `/admins/${id}`
          : role === 'teacher'
            ? `/teachers/${id}`
            : `/students/${id}`

      await api(endpoint, { method: 'DELETE' })
    } catch (error: any) {
      throw new Error(
        error?.data?.detail || 'Xóa thất bại'
      )
    }
  }

  return {
    getUsers,
    createUser,
    updateUser,
    deleteUser
  }
}
