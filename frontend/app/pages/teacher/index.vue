<script setup lang="ts">
import { Plus, Trash2, Users, Edit2 } from 'lucide-vue-next'
import type { Class } from '~/types'
import { useClasses } from '~/composables/useClasses'

definePageMeta({
  layout: 'teacher'
})

/* ================= COMPOSABLE ================= */
const {
  classes,
  loading,
  getClasses,
  getClassDetail,
  createClass,
  updateClass,
  deleteClass,
  removeStudent
} = useClasses()

/* ================= STATE ================= */
const showModal = ref(false)
const editingClass = ref<Class | null>(null)

const className = ref('')
const description = ref('')

const selectedClass = ref<Class | null>(null)

/* ================= LOAD ================= */
onMounted(() => {
  getClasses()
})

/* ================= ACTIONS ================= */
const openCreateModal = () => {
  editingClass.value = null
  className.value = ''
  description.value = ''
  showModal.value = true
}

const openEditModal = (cls: Class) => {
  editingClass.value = cls
  className.value = cls.name
  description.value = cls.description || ''
  showModal.value = true
}

const handleSubmit = async () => {
  if (!className.value.trim()) return

  if (editingClass.value) {
    await updateClass(editingClass.value.id, {
      name: className.value,
      description: description.value
    })
  } else {
    await createClass({
      name: className.value,
      description: description.value
    })
  }

  showModal.value = false
}

const handleDeleteClass = async (id: number) => {
  if (!confirm('Bạn có chắc muốn xóa lớp này?')) return
  await deleteClass(id)
}

const openStudents = async (cls: Class) => {
  selectedClass.value = await getClassDetail(cls.id)
}

const handleRemoveStudent = async (studentId: number) => {
  if (!selectedClass.value) return

  selectedClass.value = await removeStudent(
    selectedClass.value.id,
    studentId
  )
}
</script>

<template>
  <div class="space-y-6">
    <!-- HEADER -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Quản lý lớp học</h1>
      <button
        class="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        @click="openCreateModal"
      >
        <Plus class="h-4 w-4" />
        Tạo lớp
      </button>
    </div>

    <!-- LOADING -->
    <div v-if="loading" class="text-gray-500">
      Đang tải dữ liệu...
    </div>

    <!-- CLASS LIST -->
    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="cls in classes"
        :key="cls.id"
        class="rounded-xl border bg-white p-4 shadow-sm"
      >
        <div class="flex items-start justify-between">
          <div>
            <h2 class="text-lg font-semibold">{{ cls.name }}</h2>
            <p class="text-sm text-gray-500">
              {{ cls.description || 'Không có mô tả' }}
            </p>
          </div>

          <div class="flex gap-2">
            <button
              class="text-blue-600 hover:text-blue-800"
              @click="openEditModal(cls)"
            >
              <Edit2 class="h-4 w-4" />
            </button>

            <button
              class="text-red-600 hover:text-red-800"
              @click="handleDeleteClass(cls.id)"
            >
              <Trash2 class="h-4 w-4" />
            </button>
          </div>
        </div>

        <button
          class="mt-3 flex items-center gap-2 text-sm text-gray-600 hover:text-black"
          @click="openStudents(cls)"
        >
          <Users class="h-4 w-4" />
          Xem sinh viên
        </button>
      </div>
    </div>

    <!-- MODAL CREATE / EDIT -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    >
      <div class="w-full max-w-md rounded-xl bg-white p-6">
        <h2 class="mb-4 text-lg font-semibold">
          {{ editingClass ? 'Sửa lớp' : 'Tạo lớp mới' }}
        </h2>

        <div class="space-y-3">
          <input
            v-model="className"
            placeholder="Tên lớp"
            class="w-full rounded-lg border px-3 py-2"
          />

          <textarea
            v-model="description"
            placeholder="Mô tả"
            class="w-full rounded-lg border px-3 py-2"
          />
        </div>

        <div class="mt-4 flex justify-end gap-2">
          <button
            class="rounded-lg border px-4 py-2"
            @click="showModal = false"
          >
            Hủy
          </button>
          <button
            class="rounded-lg bg-blue-600 px-4 py-2 text-white"
            @click="handleSubmit"
          >
            Lưu
          </button>
        </div>
      </div>
    </div>

    <!-- STUDENT LIST -->
    <div
      v-if="selectedClass"
      class="fixed inset-0 z-40 flex items-center justify-center bg-black/40"
    >
      <div class="w-full max-w-lg rounded-xl bg-white p-6">
        <h2 class="mb-4 text-lg font-semibold">
          Sinh viên – {{ selectedClass.name }}
        </h2>

        <div
          v-if="!selectedClass.students || !selectedClass.students.length"
          class="text-gray-500"
        >
          Chưa có sinh viên
        </div>

        <ul v-else class="space-y-2">
          <li
            v-for="st in selectedClass.students"
            :key="st.id"
            class="flex items-center justify-between rounded border px-3 py-2"
          >
            <span>{{ st.full_name }}</span>
            <button
              class="text-red-600 hover:text-red-800"
              @click="handleRemoveStudent(st.id)"
            >
              <Trash2 class="h-4 w-4" />
            </button>
          </li>
        </ul>

        <div class="mt-4 text-right">
          <button
            class="rounded-lg border px-4 py-2"
            @click="selectedClass = null"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
