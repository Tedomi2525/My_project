import type { User } from '~/types'
import { jwtDecode } from 'jwt-decode'
import { authService } from '~/services/auth'

export const useAuth = () => {
  // ----------------- STATE -----------------
  const user = useState<User | null>('user', () => null)
  const tokenCookie = useCookie<string | null>('token', {
    maxAge: 60 * 60 * 24, // 1 ngày
    sameSite: 'lax'
  })

  const router = useRouter()

  // ----------------- LOGIN -----------------
  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await authService.login({ username, password })
      tokenCookie.value = response.access_token

      const loggedUser: User = {
        id: Number(response.user_id),
        username,
        fullName: response.full_name,
        email: response.email ?? undefined,
        role: response.role,
        studentId: response.student_id ?? undefined
      }
      user.value = loggedUser 
      

      console.log('✅ USER SAU KHI SET:', user.value)
      console.log('✅ USER ID:', user.value.id)

      // Điều hướng theo role
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
      console.error('Login error:', error)
      return false
    }
  }

  // ----------------- LOGOUT -----------------
  const logout = async () => {
    user.value = null
    tokenCookie.value = null
    await router.push('/login')
  }

  // ----------------- RESTORE USER -----------------
  const fetchUser = async () => {
    const token = tokenCookie.value
    if (!token || user.value) return

    try {
      // Nếu backend có /me
      // const response = await $fetch('/api/me', {
      //   headers: { Authorization: `Bearer ${token}` }
      // })
      // user.value = { ...response }

      // Hoặc decode JWT trực tiếp
      const payload: any = jwtDecode(token)
      user.value = {
        id: payload.user_id,
        username: payload.username,
        fullName: payload.full_name,
        email: payload.email,
        role: payload.role,
        studentId: payload.student_id
      }
    } catch (error) {
      console.error('Không lấy được thông tin user:', error)
      await logout()
    }
  }

  // ----------------- COMPUTED -----------------
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
