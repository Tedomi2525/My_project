<script setup lang="ts">
import { Search, UserPlus, Edit2, Trash2, Key, Lock, Unlock } from 'lucide-vue-next'
import type { User } from '~/types'
import { useUsers } from '~/composables/useUsers'

type ManagedRole = 'teacher' | 'student'

const props = defineProps<{
  role: ManagedRole
}>()

const { getUsers, createUser, updateUser, deleteUser } = useUsers()

const users = ref<User[]>([])
const searchTerm = ref('')
const showModal = ref(false)
const editingUser = ref<User | null>(null)

const roleLabel = computed(() => props.role === 'teacher' ? 'giáo viên' : 'sinh viên')
const roleTitle = computed(() => props.role === 'teacher' ? 'Giáo viên' : 'Sinh viên')
const roleBadgeClass = computed(() => props.role === 'teacher' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700')

const formData = reactive({
  fullName: '',
  email: ''
})

const normalizeUser = (u: any): User => ({
  id: u.id,
  username: u.username,
  email: u.email,
  role: u.role,
  fullName: u.full_name ?? u.fullName ?? '',
  studentId: u.student_id ?? u.studentId ?? ''
})

const loadUsers = async () => {
  try {
    const data: any[] = await getUsers()
    users.value = data.map(normalizeUser).filter(u => u.role === props.role)
  } catch (err) {
    console.error(`Lỗi load ${roleLabel.value}:`, err)
  }
}

onMounted(loadUsers)

watch(() => props.role, loadUsers)

const filteredUsers = computed(() => {
  const kw = (searchTerm.value ?? '').toLowerCase()
  return users.value.filter(u =>
    (u.fullName ?? '').toLowerCase().includes(kw) ||
    u.username.toLowerCase().includes(kw) ||
    (u.email ?? '').toLowerCase().includes(kw)
  )
})

const resetForm = () => Object.assign(formData, {
  fullName: '',
  email: ''
})

const handleAddUser = () => {
  editingUser.value = null
  resetForm()
  showModal.value = true
}

const handleEditUser = (user: User) => {
  editingUser.value = user
  Object.assign(formData, {
    fullName: user.fullName,
    email: user.email ?? ''
  })
  showModal.value = true
}

const handleDeleteUser = async (user: User) => {
  if (!confirm(`Bạn có chắc chắn muốn xóa ${roleLabel.value} này?`)) return

  try {
    await deleteUser(user.id, props.role)
    await loadUsers()
  } catch (err: any) {
    alert(err.message || 'Xóa thất bại')
  }
}

const handleAccountLock = async (user: User, locked: boolean) => {
  try {
    const config = useRuntimeConfig()
    const token = useCookie<string | null>('token')
    await $fetch(`/admin/accounts/${props.role}/${user.id}/lock`, {
      method: 'PATCH',
      baseURL: config.public.apiBase,
      headers: { Authorization: `Bearer ${token.value || ''}` },
      body: { locked }
    })
    alert(locked ? 'Đã khóa tài khoản' : 'Đã mở khóa tài khoản')
  } catch (err: any) {
    alert(err?.data?.detail || 'Không thể cập nhật trạng thái tài khoản')
  }
}

const handleResetPassword = async (user: User) => {
  if (!confirm(`Reset mật khẩu cho ${user.fullName}?`)) return

  try {
    const newPassword = `${user.username}@`
    await updateUser(user.id, props.role, { password: newPassword })
    alert(`Mật khẩu mới của ${user.username}: ${newPassword}`)
  } catch (err: any) {
    alert(err.message || 'Reset mật khẩu thất bại')
  }
}

const handleSubmit = async () => {
  try {
    if (editingUser.value) {
      await updateUser(editingUser.value.id, props.role, {
        full_name: formData.fullName,
        email: formData.email
      } as any)
    } else {
      await createUser({
        fullName: formData.fullName,
        email: formData.email,
        role: props.role
      })
    }

    showModal.value = false
    resetForm()
    await loadUsers()
  } catch (err: any) {
    alert(err.message || 'Có lỗi xảy ra')
  }
}
</script>

<template>
  <div>
    <div class="mb-6 flex justify-between gap-4">
      <div class="relative max-w-md flex-1">
        <Search class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
        <input
          v-model="searchTerm"
          :placeholder="`Tìm ${roleLabel}...`"
          class="input-field pl-10"
        />
      </div>
      <button
        type="button"
        @click="handleAddUser"
        class="btn-primary"
      >
        <UserPlus class="h-5 w-5" />
        Thêm {{ roleLabel }}
      </button>
    </div>

    <div class="panel-card overflow-hidden p-0">
      <table class="w-full">
        <thead class="border-b bg-gray-50">
          <tr>
            <th class="p-4 text-left">Họ tên</th>
            <th class="p-4 text-left">Mã đăng nhập</th>
            <th class="p-4 text-left">Email</th>
            <th class="p-4 text-left">Vai trò</th>
            <th class="p-4 text-left">Mật khẩu mặc định</th>
            <th class="p-4 text-right">Thao tác</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="u in filteredUsers"
            :key="u.id"
            class="border-b last:border-0 hover:bg-gray-50"
          >
            <td class="p-4 font-medium">{{ u.fullName }}</td>
            <td class="p-4">{{ u.username }}</td>
            <td class="p-4 text-gray-600">{{ u.email || '-' }}</td>
            <td class="p-4">
              <span :class="['rounded-full px-3 py-1 text-sm font-medium', roleBadgeClass]">
                {{ roleTitle }}
              </span>
            </td>
            <td class="p-4 font-mono text-sm">{{ `${u.username}@` }}</td>
            <td class="flex justify-end gap-2 p-4">
              <button type="button" @click="handleAccountLock(u, true)" class="rounded p-2 text-red-700 hover:bg-red-50" title="Khóa tài khoản">
                <Lock class="h-4 w-4" />
              </button>
              <button type="button" @click="handleAccountLock(u, false)" class="rounded p-2 text-green-700 hover:bg-green-50" title="Mở khóa tài khoản">
                <Unlock class="h-4 w-4" />
              </button>
              <button
                type="button"
                @click="handleResetPassword(u)"
                class="rounded p-2 text-orange-600 hover:bg-orange-50"
                title="Reset mật khẩu"
              >
                <Key class="h-4 w-4" />
              </button>
              <button
                type="button"
                @click="handleEditUser(u)"
                class="rounded p-2 text-blue-600 hover:bg-blue-50"
                title="Sửa"
              >
                <Edit2 class="h-4 w-4" />
              </button>
              <button
                type="button"
                @click="handleDeleteUser(u)"
                class="rounded p-2 text-red-600 hover:bg-red-50"
                title="Xóa"
              >
                <Trash2 class="h-4 w-4" />
              </button>
            </td>
          </tr>

          <tr v-if="filteredUsers.length === 0">
            <td colspan="6" class="p-6 text-center text-gray-500">
              Không có dữ liệu
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      v-if="showModal"
      class="modal-overlay"
    >
      <div class="modal-card max-w-md">
        <h2 class="mb-4 text-xl font-bold">
          {{ editingUser ? `Sửa ${roleLabel}` : `Thêm ${roleLabel}` }}
        </h2>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <input
            v-model="formData.fullName"
            class="input-field"
            placeholder="Họ tên"
            required
          />
          <input
            v-model="formData.email"
            type="email"
            class="input-field"
            placeholder="Email"
          />

          <div class="rounded-lg border border-blue-100 bg-blue-50 p-3 text-sm text-blue-800">
            Tài khoản sẽ được tạo với vai trò {{ roleLabel }}. Mã đăng nhập và mật khẩu mặc định được hệ thống tự sinh.
          </div>

          <div class="flex gap-3 pt-4">
            <button type="button" @click="showModal = false" class="btn-secondary flex-1">
              Hủy
            </button>
            <button type="submit" class="btn-primary flex-1">
              {{ editingUser ? 'Cập nhật' : 'Thêm' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
