<script setup lang="ts">
import UserManagement from '~/components/admin/UserManagement.vue'

definePageMeta({ layout: 'admin' })
</script>

<template>
  <UserManagement role="teacher" />
</template>
