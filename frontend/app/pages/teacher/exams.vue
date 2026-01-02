<script setup lang="ts">
import { Search, Plus, Edit2, Trash2, Play, Square, Eye, EyeOff } from 'lucide-vue-next'
import type { Exam, Question } from '~/types'

definePageMeta({ layout: 'teacher' })
const teacherId = 'teacher1'

// --- Mock Data ---
const mockQuestions: Question[] = [
    { id: 'q1', content: 'HTML là gì?', options: [], correctAnswer: 0, createdBy: 't1', createdAt: new Date() },
    { id: 'q2', content: 'CSS là gì?', options: [], correctAnswer: 0, createdBy: 't1', createdAt: new Date() }
]
const mockStudents = [{ id: 'student1', name: 'Lê Văn Minh', studentId: 'SV001' }, { id: 'student2', name: 'Nguyễn Thị Hương', studentId: 'SV002' }]

// --- State ---
const exams = ref<Exam[]>([
  {
    id: 'exam1', title: 'Kiểm tra giữa kỳ', duration: 60,
    startTime: new Date('2024-02-01T08:00:00'), endTime: new Date('2024-02-01T10:00:00'),
    questions: ['q1'], allowedStudents: ['student1'], status: 'active',
    showAnswers: true, createdBy: 'teacher1', password: 'web123'
  }
])
const searchTerm = ref('')
const showModal = ref(false)
const editingExam = ref<Exam | null>(null)

// Form data (Dùng string cho date để bind vào input)
const formData = reactive({
  title: '', duration: 60, startTime: '', endTime: '',
  questions: [] as string[], allowedStudents: [] as string[],
  showAnswers: true, password: ''
})

// --- Helpers ---
const formatDateForInput = (date: Date | string) => {
    return new Date(date).toISOString().slice(0, 16) // Cắt lấy YYYY-MM-DDTHH:mm
}

const handleAddExam = () => {
  editingExam.value = null
  Object.assign(formData, { title: '', duration: 60, startTime: '', endTime: '', questions: [], allowedStudents: [], showAnswers: true, password: '' })
  showModal.value = true
}

const handleEditExam = (exam: Exam) => {
  editingExam.value = exam
  Object.assign(formData, {
    title: exam.title,
    duration: exam.duration,
    startTime: formatDateForInput(exam.startTime),
    endTime: formatDateForInput(exam.endTime),
    questions: [...exam.questions],
    allowedStudents: [...exam.allowedStudents],
    showAnswers: exam.showAnswers,
    password: exam.password || ''
  })
  showModal.value = true
}

const handleSubmit = () => {
    const payload = {
        ...formData,
        startTime: new Date(formData.startTime), // Convert back to Date object
        endTime: new Date(formData.endTime)
    }
    if(editingExam.value) {
        exams.value = exams.value.map(e => e.id === editingExam.value?.id ? {...e, ...payload} : e)
    } else {
        exams.value.push({ id: `exam_${Date.now()}`, ...payload, status: 'draft', createdBy: teacherId })
    }
    showModal.value = false
}

const toggleSelection = (list: string[], item: string) => {
    const idx = list.indexOf(item)
    if (idx > -1) list.splice(idx, 1)
    else list.push(item)
}

const getStatusBadge = (status: string) => {
    const map: any = {
        draft: { cls: 'bg-gray-100 text-gray-700', lbl: 'Nháp' },
        active: { cls: 'bg-green-100 text-green-700', lbl: 'Đang diễn ra' },
        ended: { cls: 'bg-red-100 text-red-700', lbl: 'Đã kết thúc' }
    }
    return map[status]
}
</script>

<template>
  <div>
    <div class="mb-6 flex justify-between">
        <div class="flex-1 max-w-md">
            <input type="text" v-model="searchTerm" placeholder="Tìm đề thi..." class="w-full px-4 py-2 border rounded-lg" />
        </div>
        <button @click="handleAddExam" class="bg-blue-600 text-white px-4 py-2 rounded-lg flex gap-2 items-center"><Plus class="w-5 h-5"/> Tạo đề thi</button>
    </div>

    <div class="space-y-4">
        <div v-for="exam in exams" :key="exam.id" class="bg-white rounded-lg shadow p-6">
            <div class="flex justify-between items-start">
                <div>
                    <div class="flex items-center gap-3 mb-2">
                        <h3 class="font-bold text-lg">{{ exam.title }}</h3>
                        <span :class="['px-3 py-1 rounded-full text-sm', getStatusBadge(exam.status).cls]">{{ getStatusBadge(exam.status).lbl }}</span>
                    </div>
                    <div class="text-sm text-gray-600">
                         <p>Thời gian: {{ exam.duration }} phút | Số câu: {{ exam.questions.length }}</p>
                         <p>Mở: {{ new Date(exam.startTime).toLocaleString('vi-VN') }}</p>
                    </div>
                </div>
                <div class="flex gap-2">
                    <button v-if="exam.status === 'draft'" @click="exam.status = 'active'" class="bg-green-50 text-green-700 px-3 py-2 rounded flex gap-1 items-center"><Play class="w-4 h-4"/> Kích hoạt</button>
                    <button @click="handleEditExam(exam)" class="text-blue-600 p-2 bg-blue-50 rounded"><Edit2 class="w-4 h-4"/></button>
                </div>
            </div>
        </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 overflow-y-auto">
        <div class="bg-white rounded-lg p-6 w-full max-w-4xl my-8">
            <h2 class="mb-4 font-bold text-xl">{{ editingExam ? 'Sửa đề thi' : 'Tạo đề thi mới' }}</h2>
            <form @submit.prevent="handleSubmit" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="md:col-span-2">
                    <label>Tên đề thi</label>
                    <input type="text" v-model="formData.title" class="w-full border p-2 rounded" required />
                </div>
                <div><label>Bắt đầu</label><input type="datetime-local" v-model="formData.startTime" class="w-full border p-2 rounded" required /></div>
                <div><label>Kết thúc</label><input type="datetime-local" v-model="formData.endTime" class="w-full border p-2 rounded" required /></div>
                
                <div class="md:col-span-2 grid grid-cols-2 gap-4">
                    <div class="border p-4 rounded h-60 overflow-y-auto">
                        <p class="font-bold mb-2">Chọn câu hỏi</p>
                        <div v-for="q in mockQuestions" :key="q.id" class="flex gap-2 items-center mb-2">
                            <input type="checkbox" :checked="formData.questions.includes(q.id)" @change="toggleSelection(formData.questions, q.id)" />
                            <span>{{ q.content }}</span>
                        </div>
                    </div>
                    <div class="border p-4 rounded h-60 overflow-y-auto">
                         <p class="font-bold mb-2">Chọn sinh viên</p>
                        <div v-for="s in mockStudents" :key="s.id" class="flex gap-2 items-center mb-2">
                            <input type="checkbox" :checked="formData.allowedStudents.includes(s.id)" @change="toggleSelection(formData.allowedStudents, s.id)" />
                            <span>{{ s.name }}</span>
                        </div>
                    </div>
                </div>

                <div class="md:col-span-2 flex gap-3 mt-4">
                    <button type="button" @click="showModal = false" class="flex-1 border py-2 rounded">Hủy</button>
                    <button type="submit" class="flex-1 bg-blue-600 text-white py-2 rounded">Lưu</button>
                </div>
            </form>
        </div>
    </div>
  </div>
</template>