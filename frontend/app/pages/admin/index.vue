<script setup lang="ts">
import { Search, UserPlus, Edit2, Trash2, Key } from 'lucide-vue-next'
import type { User } from '~/types'
import { useUsers } from '~/composables/useUsers'

definePageMeta({ layout: 'admin' })

// ================== API ==================
const { getUsers, createUser, updateUser, deleteUser } = useUsers()

// ================== STATE ==================
const users = ref<User[]>([])
const searchTerm = ref('')
const showModal = ref(false)
const editingUser = ref<User | null>(null)

const formData = reactive({
  username: '',
  password: '',
  fullName: '',
  email: '',
  role: 'student' as 'admin' | 'teacher' | 'student',
  studentId: ''
})

// ================== LOAD ==================
const loadUsers = async () => {
  users.value = await getUsers()
}

onMounted(() => {
  loadUsers()
})

// ================== COMPUTED ==================
const filteredUsers = computed(() => {
  const keyword = (searchTerm.value ?? '').toLowerCase()

  return users.value.filter(u =>
    u.fullName.toLowerCase().includes(keyword) ||
    u.username.toLowerCase().includes(keyword) ||
    (u.email ?? '').toLowerCase().includes(keyword)
  )
})

// ================== UI HELPERS ==================
const getRoleBadge = (role: 'admin' | 'teacher' | 'student') => {
  const map = {
    admin: { cls: 'bg-purple-100 text-purple-700', lbl: 'Quản trị viên' },
    teacher: { cls: 'bg-blue-100 text-blue-700', lbl: 'Giảng viên' },
    student: { cls: 'bg-green-100 text-green-700', lbl: 'Sinh viên' }
  }
  return map[role]
}

// ================== ACTIONS ==================
const resetForm = () => {
  Object.assign(formData, {
    username: '',
    password: '',
    fullName: '',
    email: '',
    role: 'student',
    studentId: ''
  })
}

const handleAddUser = () => {
  editingUser.value = null
  resetForm()
  showModal.value = true
}

const handleEditUser = (user: User) => {
  editingUser.value = user
  Object.assign(formData, {
    username: user.username,
    password: '',
    fullName: user.fullName,
    email: user.email ?? '',
    role: user.role,
    studentId: user.studentId ?? ''
  })
  showModal.value = true
}

const handleDeleteUser = async (id: number) => {
  if (!confirm('Bạn có chắc chắn muốn xóa user này?')) return
  await deleteUser(id)
  await loadUsers()
}

const handleResetPassword = async (user: User) => {
  if (!confirm(`Reset mật khẩu cho ${user.fullName}?`)) return
  alert(`Mật khẩu mới của ${user.username}: password123`)
}

const handleSubmit = async () => {
  if (editingUser.value) {
    // ✅ FIX: dùng biến tạm để TS chắc chắn không undefined
    const user = editingUser.value

    await updateUser(user.id, {
      fullName: formData.fullName,
      email: formData.email,
      role: formData.role,
      studentId: formData.studentId
    })
  } else {
    await createUser({
      username: formData.username,
      password: formData.password,
      fullName: formData.fullName,
      email: formData.email,
      role: formData.role,
      studentId: formData.studentId
    })
  }

  showModal.value = false
  await loadUsers()
}
</script>

<template>
  <div>
    <!-- SEARCH + ADD -->
    <div class="mb-6 flex justify-between gap-4">
      <div class="relative flex-1 max-w-md">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          v-model="searchTerm"
          placeholder="Tìm người dùng..."
          class="w-full pl-10 pr-4 py-2 border rounded-lg"
        />
      </div>
      <button
        @click="handleAddUser"
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        <UserPlus class="w-5 h-5" /> Thêm tài khoản
      </button>
    </div>

    <!-- TABLE -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="p-4 text-left">Họ tên</th>
            <th class="p-4 text-left">Username</th>
            <th class="p-4 text-left">Email</th>
            <th class="p-4 text-left">Vai trò</th>
            <th class="p-4 text-left">Mã SV</th>
            <th class="p-4 text-right">Thao tác</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="u in filteredUsers"
            :key="u.id"
            class="hover:bg-gray-50 border-b last:border-0"
          >
            <td class="p-4 font-medium">{{ u.fullName }}</td>
            <td class="p-4">{{ u.username }}</td>
            <td class="p-4 text-gray-600">{{ u.email || '-' }}</td>
            <td class="p-4">
              <span
                :class="[
                  'px-3 py-1 rounded-full text-sm font-medium',
                  getRoleBadge(u.role).cls
                ]"
              >
                {{ getRoleBadge(u.role).lbl }}
              </span>
            </td>
            <td class="p-4 font-mono text-sm">{{ u.studentId || '-' }}</td>
            <td class="p-4 flex justify-end gap-2">
              <button
                @click="handleResetPassword(u)"
                class="p-2 text-orange-600 hover:bg-orange-50 rounded"
              >
                <Key class="w-4 h-4" />
              </button>
              <button
                @click="handleEditUser(u)"
                class="p-2 text-blue-600 hover:bg-blue-50 rounded"
              >
                <Edit2 class="w-4 h-4" />
              </button>
              <button
                @click="handleDeleteUser(u.id)"
                class="p-2 text-red-600 hover:bg-red-50 rounded"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- MODAL -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="font-bold text-xl mb-4">
          {{ editingUser ? 'Sửa tài khoản' : 'Thêm tài khoản' }}
        </h2>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <input v-model="formData.fullName" class="w-full border p-2 rounded" placeholder="Họ tên" />
          <input v-model="formData.username" class="w-full border p-2 rounded" placeholder="Username" />
          <input
            type="password"
            v-model="formData.password"
            class="w-full border p-2 rounded"
            placeholder="Mật khẩu"
            :required="!editingUser"
          />
          <input type="email" v-model="formData.email" class="w-full border p-2 rounded" placeholder="Email" />

          <select v-model="formData.role" class="w-full border p-2 rounded">
            <option value="student">Sinh viên</option>
            <option value="teacher">Giảng viên</option>
            <option value="admin">Quản trị viên</option>
          </select>

          <input
            v-if="formData.role === 'student'"
            v-model="formData.studentId"
            class="w-full border p-2 rounded"
            placeholder="Mã sinh viên"
          />

          <div class="flex gap-3 pt-4">
            <button type="button" @click="showModal = false" class="flex-1 border py-2 rounded">
              Hủy
            </button>
            <button type="submit" class="flex-1 bg-blue-600 text-white py-2 rounded">
              {{ editingUser ? 'Cập nhật' : 'Thêm' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
