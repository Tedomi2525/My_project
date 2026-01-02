<script setup lang="ts">
import { Search, Plus, Edit2, Trash2, UserPlus, UserMinus, Users } from 'lucide-vue-next'
import type { Class } from '~/types'

// Sử dụng layout teacher đã định nghĩa ở trên
definePageMeta({ layout: 'teacher' })

const teacherId = 'teacher1'

// Mock Data
const mockStudents = [
  { id: 'student1', name: 'Lê Văn Minh', studentId: 'SV001' },
  { id: 'student2', name: 'Nguyễn Thị Hương', studentId: 'SV002' },
  { id: 'student3', name: 'Hoàng Minh Tuấn', studentId: 'SV003' },
  { id: 'student4', name: 'Trần Thị Mai', studentId: 'SV004' },
  { id: 'student5', name: 'Phạm Văn Nam', studentId: 'SV005' }
]

const initialClasses: Class[] = [
  { id: 'class1', name: 'Lập trình Web - Nhóm 1', teacherId: 'teacher1', students: ['student1', 'student2', 'student3'] },
  { id: 'class2', name: 'Cơ sở dữ liệu - Nhóm 2', teacherId: 'teacher1', students: ['student2', 'student4'] }
]

// State
const classes = ref<Class[]>(initialClasses)
const searchTerm = ref('')
const showModal = ref(false)
const showStudentModal = ref(false)
const editingClass = ref<Class | null>(null)
const selectedClass = ref<Class | null>(null)
const className = ref('')

// Computed
const filteredClasses = computed(() => 
  classes.value.filter(cls => cls.name.toLowerCase().includes(searchTerm.value.toLowerCase()))
)

// Actions
const handleAddClass = () => {
  editingClass.value = null
  className.value = ''
  showModal.value = true
}

const handleEditClass = (cls: Class) => {
  editingClass.value = cls
  className.value = cls.name
  showModal.value = true
}

const handleDeleteClass = (classId: string) => {
  if (confirm('Bạn có chắc chắn muốn xóa lớp học này?')) {
    classes.value = classes.value.filter(c => c.id !== classId)
  }
}

const handleSubmit = () => {
  if (editingClass.value) {
    classes.value = classes.value.map(c =>
      c.id === editingClass.value?.id ? { ...c, name: className.value } : c
    )
  } else {
    const newClass: Class = {
      id: `class_${Date.now()}`,
      name: className.value,
      teacherId,
      students: []
    }
    classes.value = [...classes.value, newClass]
  }
  showModal.value = false
}

const handleManageStudents = (cls: Class) => {
  selectedClass.value = cls
  showStudentModal.value = true
}

const handleAddStudent = (studentId: string) => {
  if (selectedClass.value) {
    // Update local selected class
    const updatedClass = {
        ...selectedClass.value,
        students: [...selectedClass.value.students, studentId]
    }
    selectedClass.value = updatedClass
    
    // Update main list
    classes.value = classes.value.map(c => c.id === updatedClass.id ? updatedClass : c)
  }
}

const handleRemoveStudent = (studentId: string) => {
  if (selectedClass.value) {
    const updatedClass = {
        ...selectedClass.value,
        students: selectedClass.value.students.filter(s => s !== studentId)
    }
    selectedClass.value = updatedClass
    classes.value = classes.value.map(c => c.id === updatedClass.id ? updatedClass : c)
  }
}

const getStudent = (id: string) => mockStudents.find(s => s.id === id)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-col sm:flex-row gap-4 justify-between">
      <div class="relative flex-1 max-w-md">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Tìm kiếm lớp học..."
          v-model="searchTerm"
          class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <button
        @click="handleAddClass"
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <Plus class="w-5 h-5" />
        Tạo lớp học mới
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="cls in filteredClasses" :key="cls.id" class="bg-white rounded-lg shadow p-6">
        <h3 class="mb-4 font-semibold text-lg">{{ cls.name }}</h3>
        <div class="flex items-center gap-2 text-gray-600 mb-4">
          <Users class="w-5 h-5" />
          <span>{{ cls.students.length }} sinh viên</span>
        </div>
        <div class="flex gap-2">
          <button @click="handleManageStudents(cls)" class="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors">
            <UserPlus class="w-4 h-4" /> Quản lý SV
          </button>
          <button @click="handleEditClass(cls)" class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"><Edit2 class="w-4 h-4" /></button>
          <button @click="handleDeleteClass(cls.id)" class="p-2 text-red-600 hover:bg-red-50 rounded-lg"><Trash2 class="w-4 h-4" /></button>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="mb-4 font-bold text-xl">{{ editingClass ? 'Sửa lớp học' : 'Tạo lớp học mới' }}</h2>
        <form @submit.prevent="handleSubmit">
          <div class="mb-4">
            <label class="block mb-2">Tên lớp học</label>
            <input type="text" v-model="className" class="w-full px-4 py-2 border rounded-lg" required />
          </div>
          <div class="flex gap-3">
            <button type="button" @click="showModal = false" class="flex-1 px-4 py-2 border rounded-lg">Hủy</button>
            <button type="submit" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg">{{ editingClass ? 'Cập nhật' : 'Tạo' }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showStudentModal && selectedClass" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <h2 class="mb-4 font-bold text-xl">Quản lý sinh viên - {{ selectedClass.name }}</h2>
        
        <div class="mb-6">
          <h3 class="mb-3 font-semibold">Sinh viên trong lớp</h3>
          <div class="space-y-2">
            <div v-for="sid in selectedClass.students" :key="sid" class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <div>
                <p>{{ getStudent(sid)?.name }}</p>
                <p class="text-sm text-gray-500">{{ getStudent(sid)?.studentId }}</p>
              </div>
              <button @click="handleRemoveStudent(sid)" class="text-red-600 p-2 hover:bg-red-50 rounded"><UserMinus class="w-4 h-4" /></button>
            </div>
             <p v-if="!selectedClass.students.length" class="text-center text-gray-500">Chưa có sinh viên</p>
          </div>
        </div>

        <div class="mb-6">
          <h3 class="mb-3 font-semibold">Thêm sinh viên</h3>
          <div class="space-y-2">
             <div v-for="s in mockStudents.filter(st => !selectedClass?.students.includes(st.id))" :key="s.id" class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <div>
                <p>{{ s.name }}</p>
                <p class="text-sm text-gray-500">{{ s.studentId }}</p>
              </div>
              <button @click="handleAddStudent(s.id)" class="text-green-600 p-2 hover:bg-green-50 rounded"><UserPlus class="w-4 h-4" /></button>
            </div>
          </div>
        </div>
        <button @click="showStudentModal = false" class="w-full bg-blue-600 text-white py-2 rounded-lg">Đóng</button>
      </div>
    </div>
  </div>
</template>