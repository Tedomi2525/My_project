<script setup lang="ts">
import { RefreshCw } from 'lucide-vue-next'

definePageMeta({ layout: 'admin' })

interface AuditItem {
  id: number
  actor_role: string
  actor_id: number
  actor_name?: string
  action: string
  entity_type: string
  entity_id?: string
  details?: Record<string, unknown>
  created_at: string
}

const config = useRuntimeConfig()
const token = useCookie<string | null>('token')
const items = ref<AuditItem[]>([])
const loading = ref(false)
const error = ref('')

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    items.value = await $fetch<AuditItem[]>('/admin/audit-logs', {
      baseURL: config.public.apiBase,
      headers: { Authorization: `Bearer ${token.value || ''}` }
    })
  } catch (err: any) {
    error.value = err?.data?.detail || 'Không thể tải nhật ký'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="panel-card">
    <div class="mb-4 flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold">Nhật ký hệ thống</h2>
        <p class="text-sm text-gray-500">Các thao tác thay đổi dữ liệu gần nhất.</p>
      </div>
      <button class="btn-secondary" :disabled="loading" @click="load">
        <RefreshCw class="h-4 w-4" /> Làm mới
      </button>
    </div>
    <p v-if="error" class="rounded bg-red-50 p-3 text-red-700">{{ error }}</p>
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="border-b bg-gray-50">
          <tr>
            <th class="p-3 text-left">Thời gian</th>
            <th class="p-3 text-left">Người thực hiện</th>
            <th class="p-3 text-left">Hành động</th>
            <th class="p-3 text-left">Đối tượng</th>
            <th class="p-3 text-left">Chi tiết</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" class="border-b">
            <td class="p-3 whitespace-nowrap">{{ new Date(item.created_at).toLocaleString('vi-VN') }}</td>
            <td class="p-3">{{ item.actor_name || `${item.actor_role} #${item.actor_id}` }}</td>
            <td class="p-3 font-medium">{{ item.action }}</td>
            <td class="p-3">{{ item.entity_type }} {{ item.entity_id ? `#${item.entity_id}` : '' }}</td>
            <td class="p-3 font-mono text-xs">{{ item.details || {} }}</td>
          </tr>
          <tr v-if="!loading && !items.length">
            <td colspan="5" class="p-6 text-center text-gray-500">Chưa có nhật ký</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
