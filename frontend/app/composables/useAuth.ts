// composables/useAuth.ts
import type { User } from '~/types'

// Mock Data (Di chuyển từ Login page sang đây để quản lý tập trung)
const MOCK_USERS: User[] = [
  { id: 'admin1', username: 'admin', password: 'admin123', fullName: 'Nguyễn Văn Admin', email: 'admin@university.edu.vn', role: 'admin' },
  { id: 'teacher1', username: 'teacher', password: 'teacher123', fullName: 'Trần Thị Lan', email: 'lan.tran@university.edu.vn', role: 'teacher' },
  { id: 'student1', username: 'student', password: 'student123', fullName: 'Lê Văn Minh', email: 'minh.le@student.edu.vn', role: 'student', studentId: 'SV001' }
]

export const useAuth = () => {
  // Sử dụng useCookie để trạng thái tồn tại sau khi refresh trang
  // 'user' là tên cookie
  const user = useCookie<User | null>('user', {
    maxAge: 60 * 60 * 24, // 1 ngày
    sameSite: 'lax'
  })

  const router = useRouter()

  // Hàm đăng nhập
  const login = (username: string, password: string): Promise<boolean> => {
    return new Promise((resolve) => {
      // Giả lập độ trễ API 1 chút cho giống thật
      setTimeout(() => {
        const foundUser = MOCK_USERS.find(u => u.username === username && u.password === password)

        if (foundUser) {
          user.value = foundUser
          
          // Điều hướng dựa trên vai trò
          if (foundUser.role === 'admin') {
            router.push('/admin')
          } else if (foundUser.role === 'teacher') {
            router.push('/teacher')
          } else {
            router.push('/student')
          }
          resolve(true)
        } else {
          resolve(false)
        }
      }, 300)
    })
  }

  // Hàm đăng xuất
  const logout = () => {
    user.value = null
    router.push('/login')
  }

  // Computed properties tiện ích
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isTeacher = computed(() => user.value?.role === 'teacher')
  const isStudent = computed(() => user.value?.role === 'student')

  return {
    user,
    login,
    logout,
    isAuthenticated,
    isAdmin,
    isTeacher,
    isStudent
  }
}