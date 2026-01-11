<script setup lang="ts">
const { fetchUser } = useAuth()
await fetchUser()
</script>
  

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
