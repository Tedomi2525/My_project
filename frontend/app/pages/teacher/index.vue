<script setup lang="ts">
import { Plus, Trash2, Users, Edit2 } from 'lucide-vue-next'
import type { Class, AvailableStudent } from '~/types'
import { useClasses } from '~/composables/useClasses'

definePageMeta({
  layout: 'teacher'
})

const { user } = useAuth()

const {
  classes,
  loading,
  getClasses,
  getClassDetail,
  createClass,
  updateClass,
  deleteClass,
  removeStudent,
  getAvailableStudents,
  addStudent
} = useClasses(
  computed(() => user.value?.id)
)

/* ================= STATE ================= */
const showModal = ref(false)
const editingClass = ref<Class | null>(null)

const className = ref('')
const description = ref('')

const selectedClass = ref<Class | null>(null)
const searchTerm = ref('')

const availableStudents = ref<any[]>([])
const selectedStudentId = ref<number | null>(null)


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
  availableStudents.value = await getAvailableStudents(cls.id)
  selectedStudentId.value = null
}

const handleRemoveStudent = async (studentId: number) => {
  if (!selectedClass.value) return

  selectedClass.value = await removeStudent(
    selectedClass.value.id,
    studentId
  )
  selectedStudentId.value = null
}
const handleAddStudent = async () => {
  if (!selectedClass.value || selectedStudentId.value === null) return

  selectedClass.value = await addStudent(
    selectedClass.value.id,
    selectedStudentId.value
  )

  availableStudents.value = await getAvailableStudents(
    selectedClass.value.id
  )

  selectedStudentId.value = null
}



</script>

<template>
  <div>
    <!-- Search + Add -->
    <div class="mb-6 flex flex-col sm:flex-row gap-4 justify-between">
      <div class="relative flex-1 max-w-md">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input type="text" placeholder="Tìm kiếm lớp học..." v-model="searchTerm" class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg
                 focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      <button @click="openCreateModal" class="flex items-center gap-2 px-4 py-2 bg-blue-600
               text-white rounded-lg hover:bg-blue-700 transition-colors">
        <Plus class="w-5 h-5" />
        Tạo lớp học mới
      </button>
    </div>

    <!-- LOADING -->
    <div v-if="loading" class="text-gray-500">
      Đang tải dữ liệu...
    </div>

    <!-- Class list -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="cls in classes" :key="cls.id" class="bg-white rounded-lg shadow p-6">
        <h3 class="mb-2 font-semibold text-lg">
          {{ cls.name }}
        </h3>

        <p class="mb-4 text-sm text-gray-500">
          {{ cls.description || 'Không có mô tả' }}
        </p>

        <div class="flex items-center gap-2 text-gray-600 mb-4">
          <Users class="w-5 h-5" />
          <span>
            {{ cls.students?.length || 0 }} sinh viên
          </span>
        </div>

        <div class="flex gap-2">
          <button @click="openStudents(cls)" class="flex-1 flex items-center justify-center gap-2 px-3 py-2
                   bg-green-50 text-green-700 rounded-lg
                   hover:bg-green-100 transition-colors">
            <UserPlus class="w-4 h-4" />
            Quản lý SV
          </button>

          <button @click="openEditModal(cls)" class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg">
            <Edit2 class="w-4 h-4" />
          </button>

          <button @click="handleDeleteClass(cls.id)" class="p-2 text-red-600 hover:bg-red-50 rounded-lg">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- CREATE / EDIT MODAL -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center
             justify-center p-4 z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="mb-4 font-bold text-xl">
          {{ editingClass ? 'Sửa lớp học' : 'Tạo lớp học mới' }}
        </h2>

        <div class="mb-4">
          <label class="block mb-2">Tên lớp học</label>
          <input v-model="className" class="w-full px-4 py-2 border rounded-lg" />
        </div>

        <div class="mb-4">
          <label class="block mb-2">Mô tả</label>
          <textarea v-model="description" class="w-full px-4 py-2 border rounded-lg" />
        </div>

        <div class="flex gap-3">
          <button @click="showModal = false" class="flex-1 px-4 py-2 border rounded-lg">
            Hủy
          </button>

          <button @click="handleSubmit" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg">
            {{ editingClass ? 'Cập nhật' : 'Tạo' }}
          </button>
        </div>
      </div>
    </div>

    <!-- STUDENT MODAL -->
    <div v-if="selectedClass" class="fixed inset-0 bg-black/50 flex items-center
             justify-center p-4 z-40">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h2 class="mb-4 font-bold text-xl">
          Quản lý sinh viên – {{ selectedClass.name }}
        </h2>

        <p v-if="!selectedClass.students || !selectedClass.students.length" class="text-center text-gray-500">
          Chưa có sinh viên
        </p>

        <div v-else class="space-y-2">
          <div v-for="st in selectedClass.students" :key="st.id" class="flex justify-between items-center p-3
                   bg-gray-50 rounded-lg">
            <span>{{ st.full_name }}</span>

            <button @click="handleRemoveStudent(st.id)" class="text-red-600 p-2 hover:bg-red-50 rounded">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
        <!-- ADD STUDENT -->
        <div class="mb-4 flex gap-2">
          <select v-model="selectedStudentId" class="flex-1 border px-3 py-2 rounded-lg">
            <option disabled value="">-- Chọn sinh viên --</option>

            <option v-for="st in availableStudents" :key="st.id" :value="st.id">
              {{ st.full_name }} ({{ st.student_code || 'N/A' }})
            </option>
          </select>


          <button @click="handleAddStudent" class="px-4 py-2 bg-green-600 text-white rounded-lg">
            Thêm
          </button>
        </div>
        <button @click="selectedClass = null" class="mt-4 w-full bg-blue-600 text-white py-2 rounded-lg">
          Đóng
        </button>
      </div>
    </div>
  </div>
</template>
