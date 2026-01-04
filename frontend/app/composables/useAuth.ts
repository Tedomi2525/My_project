import { authService } from '~/services/auth'
import type { User } from '~/types'

export const useAuth = () => {
  // User state (global, SSR-safe)
  const user = useState<User | null>('user', () => null)

  // JWT token
  const tokenCookie = useCookie<string | null>('token', {
    maxAge: 60 * 60 * 24, // 1 ngày
    sameSite: 'lax'
  })

  const router = useRouter()

  // ================= LOGIN =================
  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await authService.login({ username, password })

      // Lưu token
      tokenCookie.value = response.access_token

      // Gán user (KHÔNG có password)
      const loggedUser: User = {
        id: Number(response.user_id),
        username,
        fullName: response.full_name,
        email: response.email ?? undefined, // (Xem sửa lỗi 2 bên dưới)
        role: response.role,
        studentId: response.student_id ?? undefined
      }

      user.value = loggedUser
      console.log("🔥 Role nhận được từ Server:", loggedUser.role); // <-- Thêm dòng này
      // Điều hướng theo role (user.value chắc chắn KHÔNG null ở đây)
      switch (loggedUser.role) {
        case 'admin':
          await router.push('/admin')
          break
        case 'teacher':
          await router.push('/teacher')
          break
        case 'student':
          await router.push('/student')
          break
      }

      return true
    } catch (error) {
      console.error('Lỗi đăng nhập:', error)
      return false
    }
  }

  // ================= LOGOUT =================
  const logout = async () => {
    user.value = null
    tokenCookie.value = null
    await router.push('/login')
  }

  // ================= FETCH USER (OPTIONAL) =================
  const fetchUser = async () => {
    if (!tokenCookie.value || user.value) return

    try {
      // Sau này gọi API /me ở backend
    } catch (error) {
      await logout()
    }
  }

  // ================= COMPUTED =================
  const isAuthenticated = computed(() => !!user.value)
  const role = computed(() => user.value?.role ?? null)

  const isAdmin = computed(() => role.value === 'admin')  
  const isTeacher = computed(() => role.value === 'teacher')
  const isStudent = computed(() => role.value === 'student')

  return {
    user,
    role,
    login,
    logout,
    fetchUser,
    isAuthenticated,
    isAdmin,
    isTeacher,
    isStudent
  }
}
