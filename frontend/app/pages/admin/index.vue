<script setup lang="ts">
import { Search, UserPlus, Edit2, Trash2, Key } from 'lucide-vue-next'
import type { User } from '~/types' // Import interface User nếu đã define ở bước trước

definePageMeta({ layout: 'admin' })

// Mock Data
const initialUsers: User[] = [
  { id: 'admin1', username: 'admin', password: 'admin123', fullName: 'Nguyễn Văn Admin', email: 'admin@edu.vn', role: 'admin' },
  { id: 'teacher1', username: 'teacher', password: 'teacher123', fullName: 'Trần Thị Lan', email: 'lan.tran@edu.vn', role: 'teacher' },
  { id: 'student1', username: 'student', password: 'student123', fullName: 'Lê Văn Minh', email: 'minh.le@student.edu.vn', role: 'student', studentId: 'SV001' },
]

// State
const users = ref<User[]>(initialUsers)
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

// Computed Filter
const filteredUsers = computed(() => users.value.filter(u =>
  u.fullName.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
  u.username.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
  u.email.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
  (u.studentId && u.studentId.toLowerCase().includes(searchTerm.value.toLowerCase()))
))

// Actions
const resetForm = () => {
    Object.assign(formData, { username: '', password: '', fullName: '', email: '', role: 'student', studentId: '' })
}

const handleAddUser = () => {
  editingUser.value = null
  resetForm()
  showModal.value = true
}

const handleEditUser = (user: User) => {
  editingUser.value = user
  Object.assign(formData, {
      username: user.username, password: user.password,
      fullName: user.fullName, email: user.email,
      role: user.role, studentId: user.studentId || ''
  })
  showModal.value = true
}

const handleDeleteUser = (id: string) => {
  if (confirm('Bạn có chắc chắn muốn xóa?')) users.value = users.value.filter(u => u.id !== id)
}

const handleResetPassword = (user: User) => {
    if(confirm(`Reset pass cho ${user.fullName}?`)) {
        alert('Mật khẩu mới: password123')
    }
}

const handleSubmit = () => {
  if (editingUser.value) {
    users.value = users.value.map(u => u.id === editingUser.value?.id ? { ...u, ...formData } : u)
  } else {
    users.value.push({ id: `user_${Date.now()}`, ...formData })
  }
  showModal.value = false
}

const getRoleBadge = (role: string) => {
    const map: any = {
        admin: { cls: 'bg-purple-100 text-purple-700', lbl: 'Quản trị viên' },
        teacher: { cls: 'bg-blue-100 text-blue-700', lbl: 'Giảng viên' },
        student: { cls: 'bg-green-100 text-green-700', lbl: 'Sinh viên' }
    }
    return map[role] || map.student
}
</script>

<template>
  <div>
    <div class="mb-6 flex justify-between gap-4">
        <div class="relative flex-1 max-w-md">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input type="text" v-model="searchTerm" placeholder="Tìm người dùng..." class="w-full pl-10 pr-4 py-2 border rounded-lg" />
        </div>
        <button @click="handleAddUser" class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            <UserPlus class="w-5 h-5" /> Thêm tài khoản
        </button>
    </div>

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
                <tr v-for="u in filteredUsers" :key="u.id" class="hover:bg-gray-50 border-b last:border-0">
                    <td class="p-4 font-medium">{{ u.fullName }}</td>
                    <td class="p-4">{{ u.username }}</td>
                    <td class="p-4 text-gray-600">{{ u.email }}</td>
                    <td class="p-4"><span :class="['px-3 py-1 rounded-full text-sm font-medium', getRoleBadge(u.role).cls]">{{ getRoleBadge(u.role).lbl }}</span></td>
                    <td class="p-4 font-mono text-sm">{{ u.studentId || '-' }}</td>
                    <td class="p-4 flex justify-end gap-2">
                        <button @click="handleResetPassword(u)" class="p-2 text-orange-600 hover:bg-orange-50 rounded" title="Reset Pass"><Key class="w-4 h-4" /></button>
                        <button @click="handleEditUser(u)" class="p-2 text-blue-600 hover:bg-blue-50 rounded"><Edit2 class="w-4 h-4" /></button>
                        <button @click="handleDeleteUser(u.id)" class="p-2 text-red-600 hover:bg-red-50 rounded"><Trash2 class="w-4 h-4" /></button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
        <div class="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 class="font-bold text-xl mb-4">{{ editingUser ? 'Sửa tài khoản' : 'Thêm tài khoản' }}</h2>
            <form @submit.prevent="handleSubmit" class="space-y-4">
                <div><label class="block mb-1 font-medium">Họ tên</label><input type="text" v-model="formData.fullName" class="w-full border p-2 rounded" required /></div>
                <div><label class="block mb-1 font-medium">Username</label><input type="text" v-model="formData.username" class="w-full border p-2 rounded" required /></div>
                <div><label class="block mb-1 font-medium">Mật khẩu</label><input type="password" v-model="formData.password" class="w-full border p-2 rounded" :required="!editingUser" /></div>
                <div><label class="block mb-1 font-medium">Email</label><input type="email" v-model="formData.email" class="w-full border p-2 rounded" required /></div>
                
                <div>
                    <label class="block mb-1 font-medium">Vai trò</label>
                    <select v-model="formData.role" class="w-full border p-2 rounded">
                        <option value="student">Sinh viên</option>
                        <option value="teacher">Giảng viên</option>
                        <option value="admin">Quản trị viên</option>
                    </select>
                </div>

                <div v-if="formData.role === 'student'">
                    <label class="block mb-1 font-medium">Mã sinh viên</label>
                    <input type="text" v-model="formData.studentId" class="w-full border p-2 rounded" />
                </div>

                <div class="flex gap-3 pt-4">
                    <button type="button" @click="showModal = false" class="flex-1 border py-2 rounded hover:bg-gray-50">Hủy</button>
                    <button type="submit" class="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">{{ editingUser ? 'Cập nhật' : 'Thêm' }}</button>
                </div>
            </form>
        </div>
    </div>
  </div>
</template>