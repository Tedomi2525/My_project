// middleware/auth.global.ts
import type { User } from '~/types'

export default defineNuxtRouteMiddleware((to, from) => {
  // Lấy thông tin user từ cookie (đã lưu ở bước Login)
  const user = useCookie<User | null>('user')

  // 1. Nếu chưa đăng nhập
  if (!user.value) {
    // Nếu không phải trang login thì đá về login
    if (to.path !== '/login') {
      return navigateTo('/login')
    }
  } 
  // 2. Nếu đã đăng nhập
  else {
    // Nếu cố vào trang login -> đá về dashboard tương ứng
    if (to.path === '/login' || to.path === '/') {
      return navigateTo(`/${user.value.role}`)
    }

    // 3. Kiểm tra quyền truy cập (Role Guard)
    // Nếu là student mà cố vào trang /admin hoặc /teacher
    if (to.path.startsWith('/admin') && user.value.role !== 'admin') {
      return navigateTo(`/${user.value.role}`)
    }
    if (to.path.startsWith('/teacher') && user.value.role !== 'teacher') {
      return navigateTo(`/${user.value.role}`)
    }
    if (to.path.startsWith('/student') && user.value.role !== 'student') {
      return navigateTo(`/${user.value.role}`)
    }
  }
})