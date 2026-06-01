<script setup lang="ts">
import { Search, Plus, Trash2, Users, Edit2, UserMinus, UserPlus } from 'lucide-vue-next'
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
  addStudent,
  addStudents
} = useClasses(
  computed(() => user.value?.id),
  computed(() => user.value?.role)
)

/* ================= STATE ================= */
const showModal = ref(false)
const editingClass = ref<Class | null>(null)

const className = ref('')
const description = ref('')

const selectedClass = ref<Class | null>(null)
const searchTerm = ref('')

const availableStudents = ref<any[]>([])
const processingStudentId = ref<number | null>(null)
const selectedAvailableStudentIds = ref<number[]>([])
const addingSelectedStudents = ref(false)
const studentModalError = ref('')
const classStudentSearchTerm = ref('')
const availableStudentSearchTerm = ref('')

const filteredClasses = computed(() => {
  const keyword = (searchTerm.value || '').trim().toLowerCase()
  if (!keyword) return classes.value

  return classes.value.filter((cls) => {
    const name = (cls.name || '').toLowerCase()
    const description = (cls.description || '').toLowerCase()
    return name.includes(keyword) || description.includes(keyword)
  })
})

const matchesStudentKeyword = (student: AvailableStudent, keyword: string) => {
  const normalizedKeyword = keyword.trim().toLowerCase()
  if (!normalizedKeyword) return true

  return [
    student.full_name,
    student.student_code,
    'email' in student ? String(student.email || '') : ''
  ].some((value) => (value || '').toLowerCase().includes(normalizedKeyword))
}

const filteredClassStudents = computed(() => {
  if (!selectedClass.value) return []
  return selectedClass.value.students.filter((student) =>
    matchesStudentKeyword(student, classStudentSearchTerm.value)
  )
})

const filteredAvailableStudents = computed(() =>
  availableStudents.value.filter((student) =>
    matchesStudentKeyword(student, availableStudentSearchTerm.value)
  )
)

const selectableVisibleStudentIds = computed(() =>
  filteredAvailableStudents.value.map((student) => student.id)
)

const isAllVisibleStudentsSelected = computed(() => {
  const visibleIds = selectableVisibleStudentIds.value
  return visibleIds.length > 0 && visibleIds.every((id) => selectedAvailableStudentIds.value.includes(id))
})

const refreshStudentLists = async (classId: number) => {
  const updated = await getClassDetail(classId)
  selectedClass.value = updated

  const cls = classes.value.find(c => c.id === updated.id)
  if (cls) {
    cls.student_count = updated.student_count
  }

  availableStudents.value = await getAvailableStudents(updated.id)
  selectedAvailableStudentIds.value = selectedAvailableStudentIds.value.filter((id) =>
    availableStudents.value.some((student) => student.id === id)
  )
}

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
  studentModalError.value = ''
  selectedClass.value = await getClassDetail(cls.id)
  availableStudents.value = await getAvailableStudents(cls.id)
  selectedAvailableStudentIds.value = []
  classStudentSearchTerm.value = ''
  availableStudentSearchTerm.value = ''
}

const handleAddStudent = async (studentId: number) => {
  if (!selectedClass.value || processingStudentId.value) return

  processingStudentId.value = studentId
  studentModalError.value = ''
  try {
    const updated = await addStudent(
      selectedClass.value.id,
      studentId
    )
    selectedClass.value = updated

    const cls = classes.value.find(c => c.id === updated.id)
    if (cls) {
      cls.student_count = updated.student_count
    }

    availableStudents.value = await getAvailableStudents(updated.id)
    selectedAvailableStudentIds.value = selectedAvailableStudentIds.value.filter((id) => id !== studentId)
  } catch (err: any) {
    studentModalError.value = err?.data?.detail || err.message || 'Không thể thêm sinh viên vào lớp'
  } finally {
    processingStudentId.value = null
  }
}

const toggleVisibleStudents = () => {
  const visibleIds = selectableVisibleStudentIds.value
  if (isAllVisibleStudentsSelected.value) {
    selectedAvailableStudentIds.value = selectedAvailableStudentIds.value.filter((id) => !visibleIds.includes(id))
    return
  }

  selectedAvailableStudentIds.value = Array.from(new Set([
    ...selectedAvailableStudentIds.value,
    ...visibleIds
  ]))
}

const handleAddSelectedStudents = async () => {
  if (!selectedClass.value || addingSelectedStudents.value || !selectedAvailableStudentIds.value.length) return

  addingSelectedStudents.value = true
  studentModalError.value = ''
  try {
    const updated = await addStudents(selectedClass.value.id, selectedAvailableStudentIds.value)
    selectedClass.value = updated

    const cls = classes.value.find(c => c.id === updated.id)
    if (cls) {
      cls.student_count = updated.student_count
    }

    availableStudents.value = await getAvailableStudents(updated.id)
    selectedAvailableStudentIds.value = []
  } catch (err: any) {
    studentModalError.value = err?.data?.detail || err.message || 'Không thể thêm danh sách sinh viên vào lớp'
  } finally {
    addingSelectedStudents.value = false
  }
}


const handleRemoveStudent = async (studentId: number) => {
  if (!selectedClass.value || processingStudentId.value) return

  processingStudentId.value = studentId
  studentModalError.value = ''
  try {
    await removeStudent(
      selectedClass.value.id,
      studentId
    )
    await refreshStudentLists(selectedClass.value.id)
  } catch (err: any) {
    studentModalError.value = err?.data?.detail || err.message || 'Không thể cập nhật danh sách sinh viên'
  } finally {
    processingStudentId.value = null
  }
}





</script>

<template>
  <div>
    <!-- Search + Add -->
    <div class="mb-6 flex flex-col sm:flex-row gap-4 justify-between">
      <div class="relative flex-1 max-w-md">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input type="text" placeholder="Tìm kiếm lớp học..." v-model="searchTerm" class="input-field pl-10 pr-4" />
      </div>

      <button @click="openCreateModal" class="btn-primary">
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
      <div v-for="cls in filteredClasses" :key="cls.id" class="panel-card card-hover">
        <h3 class="mb-2 font-semibold text-lg">
          {{ cls.name }}
        </h3>

        <p class="mb-4 text-sm text-gray-500">
          {{ cls.description || 'Không có mô tả' }}
        </p>

        <div class="flex items-center gap-2 text-gray-600 mb-4">
          <Users class="w-5 h-5" />
          <span>
            {{ cls.student_count }} sinh viên
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
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-card max-w-md">
        <h2 class="mb-4 font-bold text-xl">
          {{ editingClass ? 'Sửa lớp học' : 'Tạo lớp học mới' }}
        </h2>

        <div class="mb-4">
          <label class="block mb-2">Tên lớp học</label>
          <input v-model="className" class="input-field" />
        </div>

        <div class="mb-4">
          <label class="block mb-2">Mô tả</label>
          <textarea v-model="description" class="textarea-field" />
        </div>

        <div class="flex gap-3">
          <button @click="showModal = false" class="btn-secondary flex-1">
            Hủy
          </button>

          <button @click="handleSubmit" class="btn-primary flex-1">
            {{ editingClass ? 'Cập nhật' : 'Tạo' }}
          </button>
        </div>
      </div>
    </div>

    <!-- STUDENT MODAL -->
    <div v-if="selectedClass" class="modal-overlay">
      <div class="modal-card max-h-[90vh] max-w-2xl overflow-y-auto">
        <h2 class="mb-1 font-bold text-xl">
          Quản lý sinh viên – {{ selectedClass.name }}
        </h2>

        <p v-if="studentModalError" class="mb-3 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {{ studentModalError }}
        </p>

        <!-- ===== STUDENTS IN CLASS ===== -->
        <p class="text-gray-600 mb-3">
          Sinh viên trong lớp ({{ selectedClass.student_count }})
        </p>

        <div v-if="selectedClass.students.length" class="relative mb-3">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            v-model="classStudentSearchTerm"
            type="text"
            placeholder="Tìm sinh viên trong lớp..."
            class="input-field pl-9 pr-4"
          />
        </div>

        <div v-if="!selectedClass.students.length" class="text-center text-gray-500 mb-4">
          Chưa có sinh viên
        </div>

        <div v-else-if="!filteredClassStudents.length" class="text-center text-gray-500 mb-6">
          Không tìm thấy sinh viên phù hợp
        </div>

        <div v-else class="space-y-2 mb-6">
          <div v-for="st in filteredClassStudents" :key="st.id"
            class="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
            <div>
              <div class="font-medium">{{ st.full_name }}</div>
              <div class="text-sm text-gray-500">
                {{ st.student_code || 'N/A' }}
              </div>
            </div>

            <button
              @click="handleRemoveStudent(st.id)"
              class="text-red-600 hover:bg-red-50 p-2 rounded disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="processingStudentId !== null"
            >
              <UserMinus class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- ===== ADD STUDENT ===== -->
        <p class="text-gray-600 mb-3">
          Thêm sinh viên
        </p>

        <div v-if="availableStudents.length" class="mb-3 flex flex-col gap-3 sm:flex-row">
          <div class="relative flex-1">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              v-model="availableStudentSearchTerm"
              type="text"
              placeholder="Tìm sinh viên để thêm..."
              class="input-field pl-9 pr-4"
            />
          </div>

          <button
            @click="handleAddSelectedStudents"
            class="btn-primary whitespace-nowrap disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="addingSelectedStudents || !selectedAvailableStudentIds.length"
          >
            <UserPlus class="w-4 h-4" />
            Thêm {{ selectedAvailableStudentIds.length || '' }}
          </button>
        </div>

        <div v-if="availableStudents.length" class="mb-3 flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm text-gray-600">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              class="h-4 w-4 accent-blue-600"
              :checked="isAllVisibleStudentsSelected"
              :disabled="!filteredAvailableStudents.length"
              @change="toggleVisibleStudents"
            />
            Chọn tất cả đang hiển thị
          </label>
          <span>{{ selectedAvailableStudentIds.length }} đã chọn</span>
        </div>

        <div v-if="!availableStudents.length" class="text-gray-500 mb-4">
          Không còn sinh viên để thêm
        </div>

        <div v-else-if="!filteredAvailableStudents.length" class="text-gray-500 mb-4">
          Không tìm thấy sinh viên phù hợp
        </div>

        <div v-else class="space-y-2 mb-6">
          <div v-for="st in filteredAvailableStudents" :key="st.id"
            class="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
            <label class="flex min-w-0 flex-1 items-center gap-3 cursor-pointer">
              <input
                v-model="selectedAvailableStudentIds"
                type="checkbox"
                class="h-4 w-4 shrink-0 accent-blue-600"
                :value="st.id"
              />
              <div class="min-w-0">
                <div class="font-medium truncate">{{ st.full_name }}</div>
                <div class="text-sm text-gray-500">
                  {{ st.student_code || 'N/A' }}
                </div>
              </div>
            </label>

            <button
              @click="handleAddStudent(st.id)"
              class="ml-3 text-green-600 hover:bg-green-50 p-2 rounded disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="processingStudentId !== null || addingSelectedStudents"
              title="Thêm sinh viên này"
            >
              <UserPlus class="w-4 h-4" />
            </button>

          </div>
        </div>

        <button @click="selectedClass = null" class="btn-primary w-full">
          Đóng
        </button>
      </div>
    </div>

  </div>
</template>
