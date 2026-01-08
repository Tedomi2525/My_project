export default defineNuxtPlugin(async () => {
  const { fetchUser } = useAuth()
  await fetchUser() // restore user khi reload
})
