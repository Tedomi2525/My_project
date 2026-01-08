// ~/composables/useUsers.ts
import type { User } from '~/types'

export const useUsers = () => {
  const config = useRuntimeConfig()
  const API_BASE = config.public.apiBase
  const token = useCookie('access_token')

  const api = <T>(url: string, options: any = {}) => {
    return $fetch<T>(url, {
      baseURL: API_BASE,
      headers: {
        Authorization: token.value ? `Bearer ${token.value}` : undefined
      },
      ...options
    })
  }

  const getUsers = async (): Promise<User[]> => {
    try {
      return await api<User[]>('/users')
    } catch (error) {
      console.error('Lỗi lấy danh sách:', error)
      return []
    }
  }

  const createUser = async (payload: {
    username: string
    password: string
    fullName: string
    email: string
    role: 'admin' | 'teacher' | 'student'
    studentId?: string
  }): Promise<User> => {
    try {
      return await api<User>('/users', {
        method: 'POST',
        body: {
          username: payload.username,
          password: payload.password,
          full_name: payload.fullName,
          email: payload.email,
          role: payload.role,
          student_id: payload.studentId
        }
      })
    } catch (error: any) {
      throw new Error(
        error?.data?.detail ||
        error?.response?._data?.detail ||
        'Thêm mới thất bại'
      )
    }
  }

  const updateUser = async (
    id: number,
    payload: Partial<Omit<User, 'id' | 'username'>>
  ): Promise<User> => {
    try {
      return await api<User>(`/users/${id}`, {
        method: 'PUT',
        body: payload
      })
    } catch (error: any) {
      throw new Error(
        error?.data?.detail ||
        error?.response?._data?.detail ||
        'Cập nhật thất bại'
      )
    }
  }

  const deleteUser = async (id: number): Promise<void> => {
    try {
      await api(`/users/${id}`, { method: 'DELETE' })
    } catch {
      throw new Error('Xóa thất bại')
    }
  }

  return {
    getUsers,
    createUser,
    updateUser,
    deleteUser
  }
}
