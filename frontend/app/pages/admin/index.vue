<script setup lang="ts">
import { Check, RefreshCw, X } from 'lucide-vue-next'
import type { AccountRequest } from '~/composables/useAccountRequests'

definePageMeta({ layout: 'admin' })

const {
  getAccountRequests,
  approveAccountRequest,
  rejectAccountRequest
} = useAccountRequests()

const accountRequests = ref<AccountRequest[]>([])
const processingRequestId = ref<number | null>(null)

const loadAccountRequests = async () => {
  try {
    accountRequests.value = await getAccountRequests()
  } catch (err) {
    console.error('Lỗi load account requests:', err)
  }
}

onMounted(loadAccountRequests)

const getRequestRoleLabel = (role: 'teacher' | 'student') => {
  return role === 'teacher' ? 'Giáo viên' : 'Sinh viên'
}

const getRequestStatusBadge = (status: AccountRequest['status']) => {
  const map = {
    pending: { cls: 'bg-yellow-50 text-yellow-700', lbl: 'Chờ duyệt' },
    approved: { cls: 'bg-green-50 text-green-700', lbl: 'Đã duyệt' },
    rejected: { cls: 'bg-red-50 text-red-700', lbl: 'Từ chối' }
  }
  return map[status]
}

const handleApproveRequest = async (request: AccountRequest) => {
  processingRequestId.value = request.id
  try {
    await approveAccountRequest(request.id)
    await loadAccountRequests()
  } catch (err: any) {
    alert(err?.data?.detail || err.message || 'Duyệt yêu cầu thất bại')
  } finally {
    processingRequestId.value = null
  }
}

const handleRejectRequest = async (request: AccountRequest) => {
  if (!confirm(`Từ chối yêu cầu của ${request.full_name}?`)) return

  processingRequestId.value = request.id
  try {
    await rejectAccountRequest(request.id)
    await loadAccountRequests()
  } catch (err: any) {
    alert(err?.data?.detail || err.message || 'Từ chối yêu cầu thất bại')
  } finally {
    processingRequestId.value = null
  }
}
</script>

<template>
  <div class="panel-card">
    <div class="mb-4 flex items-center justify-between gap-3">
      <div>
        <h2 class="text-lg font-bold">Yêu cầu tạo tài khoản</h2>
        <p class="text-sm text-gray-500">Sinh viên và giáo viên gửi yêu cầu từ màn đăng nhập.</p>
      </div>
      <button
        type="button"
        @click="loadAccountRequests"
        class="btn-secondary"
      >
        <RefreshCw class="h-4 w-4" />
        Làm mới
      </button>
    </div>

    <div v-if="accountRequests.length === 0" class="rounded-lg bg-gray-50 p-4 text-center text-sm text-gray-500">
      Chưa có yêu cầu nào đang chờ duyệt
    </div>

    <div v-else class="overflow-hidden rounded-lg border">
      <table class="w-full">
        <thead class="border-b bg-gray-50">
          <tr>
            <th class="p-3 text-left">Họ tên</th>
            <th class="p-3 text-left">Trạng thái</th>
            <th class="p-3 text-left">Vai trò</th>
            <th class="p-3 text-left">Ghi chú</th>
            <th class="p-3 text-right">Thao tác</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="request in accountRequests"
            :key="request.id"
            class="border-b last:border-0 hover:bg-gray-50"
          >
            <td class="p-3 font-medium">{{ request.full_name }}</td>
            <td class="p-3">
              <span :class="['rounded-full px-3 py-1 text-sm font-medium', getRequestStatusBadge(request.status).cls]">
                {{ getRequestStatusBadge(request.status).lbl }}
              </span>
            </td>
            <td class="p-3">
              <span class="rounded-full bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">
                {{ getRequestRoleLabel(request.role) }}
              </span>
            </td>
            <td class="p-3 text-gray-600">{{ request.note || '-' }}</td>
            <td class="p-3">
              <div class="flex justify-end gap-2">
                <button
                  v-if="request.status === 'pending'"
                  type="button"
                  @click="handleApproveRequest(request)"
                  class="rounded p-2 text-green-600 hover:bg-green-50 disabled:opacity-50"
                  :disabled="processingRequestId === request.id"
                  title="Duyệt và tạo tài khoản"
                >
                  <Check class="h-4 w-4" />
                </button>
                <button
                  v-if="request.status === 'pending'"
                  type="button"
                  @click="handleRejectRequest(request)"
                  class="rounded p-2 text-red-600 hover:bg-red-50 disabled:opacity-50"
                  :disabled="processingRequestId === request.id"
                  title="Từ chối"
                >
                  <X class="h-4 w-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
