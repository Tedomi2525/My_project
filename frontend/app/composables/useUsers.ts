// ~/composables/useUsers.ts
import type { User } from '~/types'

export const useUsers = () => {
  // 1. Lấy đường dẫn API từ cấu hình (đã cài ở bước trước)
  const config = useRuntimeConfig()
  const API_BASE = config.public.apiBase // Ví dụ: http://localhost:8000

  // 2. Hàm wrapper tiện ích để đỡ phải viết đi viết lại baseURL
  const api = <T>(url: string, options: any = {}) => {
    return $fetch<T>(url, {
      baseURL: API_BASE,
      ...options
    })
  }

  // ================= GET ALL =================
  const getUsers = async (): Promise<User[]> => {
    try {
      // Dùng $fetch trả về dữ liệu trực tiếp (không cần .value)
      return await api<User[]>('/users') 
    } catch (error) {
      console.error('Lỗi lấy danh sách:', error)
      return []
    }
  }

  // ================= CREATE =================
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
        body: payload
      })
    } catch (error: any) {
      // Ném lỗi ra để bên UI bắt được và hiện thông báo
      throw new Error(error?.data?.detail || 'Thêm mới thất bại')
    }
  }

  // ================= UPDATE =================
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
      throw new Error(error?.data?.detail || 'Cập nhật thất bại')
    }
  }

  // ================= DELETE =================
  const deleteUser = async (id: number): Promise<void> => {
    try {
      await api(`/users/${id}`, {
        method: 'DELETE'
      })
    } catch (error: any) {
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