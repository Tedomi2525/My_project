// middleware/auth.global.ts
export default defineNuxtRouteMiddleware((to) => {
  const { user } = useAuth()

  // 1️⃣ Chưa đăng nhập
  if (!user.value) {
    if (to.path !== '/login') {
      return navigateTo('/login')
    }
    return
  }

  const role = user.value.role

  // 2️⃣ Đã đăng nhập mà vào /login hoặc /
  if (to.path === '/' || to.path === '/login') {
    return navigateTo(`/${role}`)
  }

  // 3️⃣ Role guard
  if (to.path.startsWith('/admin') && role !== 'admin') {
    return navigateTo(`/${role}`)
  }

  if (to.path.startsWith('/teacher') && role !== 'teacher') {
    return navigateTo(`/${role}`)
  }

  if (to.path.startsWith('/student') && role !== 'student') {
    return navigateTo(`/${role}`)
  }
})
