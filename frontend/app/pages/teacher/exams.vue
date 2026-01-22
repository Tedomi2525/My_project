<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Search, Plus, Edit2, Trash2, Eye, EyeOff, Loader2 } from 'lucide-vue-next';
import type { Exam } from '~/types';
import { useExams } from '~/composables/useExams';

definePageMeta({
  layout: 'teacher'
});

// --- Interfaces cho dữ liệu Select ---
// (Bạn cần đảm bảo backend có API trả về đúng các field này)
interface Question {
  id: number;
  content: string;
}

interface Student {
  id: number;
  full_name: string; 
  code: string; // Mã sinh viên
}

// --- Composables ---
const { $api } = useNuxtApp(); // Dùng để gọi API questions/users trực tiếp
const { 
  exams, 
  loading, 
  error, 
  getExams, 
  getExamById, // Cần hàm này để lấy chi tiết (kèm list questions) khi sửa
  createExam, 
  updateExam, 
  deleteExam, 
  addQuestionToExam,
  removeQuestionFromExam 
} = useExams();

// --- State ---
const searchTerm = ref('');
const showModal = ref(false);
const isSubmitting = ref(false);
const editingExamId = ref<number | null>(null);

// State cho danh sách lựa chọn (thay thế Mock)
const availableQuestions = ref<Question[]>([]);
const availableStudents = ref<Student[]>([]);
const isLoadingResources = ref(false); // Loading cho list câu hỏi/sv

// Form Data
const formData = ref({
  title: '',
  description: '',
  duration_minutes: 60,
  start_time: '', 
  end_time: '',
  questions: [] as number[], // Mảng ID câu hỏi được chọn
  allowedStudents: [] as number[], // Mảng ID sinh viên được chọn
  show_answers: true,
  password: ''
});

// --- Lifecycle ---
onMounted(async () => {
  // 1. Lấy danh sách đề thi
  getExams(); 

  // 2. Lấy danh sách câu hỏi & sinh viên để fill vào modal
  try {
    isLoadingResources.value = true;
    const [resQuestions, resStudents] = await Promise.all([
      $api.get<Question[]>('/questions'), // API lấy tất cả câu hỏi
      $api.get<Student[]>('/users?role=student') // API lấy danh sách SV (tùy route bên backend của bạn)
    ]);
    availableQuestions.value = resQuestions.data || [];
    availableStudents.value = resStudents.data || [];
  } catch (err) {
    console.error('Không tải được danh sách câu hỏi/sinh viên:', err);
  } finally {
    isLoadingResources.value = false;
  }
});

// --- Computed ---
const filteredExams = computed(() => 
  exams.value.filter(exam =>
    exam.title.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
);

// --- Helpers ---
const getExamStatus = (exam: Exam) => {
  const now = new Date();
  const start = exam.start_time ? new Date(exam.start_time) : null;
  const end = exam.end_time ? new Date(exam.end_time) : null;

  if (!start) return 'draft';
  if (now < start) return 'draft';
  if (end && now > end) return 'ended';
  return 'active';
};

const formatDateDisplay = (dateStr: string | null) => {
  if (!dateStr) return '---';
  return new Date(dateStr).toLocaleString('vi-VN');
};

const formatDateForInput = (dateStr: string | null) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
  return d.toISOString().slice(0, 16);
};

// --- Methods ---

const resetForm = () => {
  editingExamId.value = null;
  formData.value = {
    title: '',
    description: '',
    duration_minutes: 60,
    start_time: '',
    end_time: '',
    questions: [],
    allowedStudents: [],
    show_answers: true,
    password: ''
  };
};

const handleAddExam = () => {
  resetForm();
  showModal.value = true;
};

const handleEditExam = async (examSummary: Exam) => {
  editingExamId.value = examSummary.id;
  
  // Mở modal trước để UI phản hồi nhanh
  showModal.value = true;
  
  try {
    // Gọi API lấy chi tiết để có danh sách câu hỏi (vì list bên ngoài có thể không trả về field này)
    const res = await getExamById(examSummary.id);
    const detail = res.data;

    formData.value = {
      title: detail.title,
      description: detail.description || '',
      duration_minutes: detail.duration_minutes,
      start_time: formatDateForInput(detail.start_time),
      end_time: formatDateForInput(detail.end_time),
      // Map dữ liệu từ API về form
      questions: detail.questions || [], 
      allowedStudents: detail.allowed_students || [],
      show_answers: detail.show_answers,
      password: '' // Không hiển thị password
    };
  } catch (e) {
    alert('Không lấy được chi tiết đề thi');
    showModal.value = false;
  }
};

const handleDeleteExam = async (examId: number) => {
  if (confirm('Bạn có chắc chắn muốn xóa đề thi này?')) {
    await deleteExam(examId);
  }
};

const handleSubmit = async () => {
  try {
    isSubmitting.value = true;
    
    // Payload cơ bản
    const payload = {
      title: formData.value.title,
      description: formData.value.description,
      duration_minutes: formData.value.duration_minutes,
      start_time: new Date(formData.value.start_time).toISOString(),
      end_time: new Date(formData.value.end_time).toISOString(),
      show_answers: formData.value.show_answers,
      ...(formData.value.password ? { password: formData.value.password } : {}),
      created_by: 1 
    };

    let examId = editingExamId.value;

    if (examId) {
      // --- UPDATE ---
      await updateExam(examId, payload);
      // TODO: Xử lý update list câu hỏi (Logic này phức tạp hơn: phải tìm diff để add/remove)
      // Tạm thời bạn có thể implement logic xóa hết cũ add lại mới ở Backend hoặc Frontend
    } else {
      // --- CREATE ---
      const newExamResponse = await createExam(payload);
      examId = newExamResponse.data.id;

      // Add Questions
      if (formData.value.questions.length > 0) {
        await Promise.all(formData.value.questions.map(qId => 
           addQuestionToExam({
             exam_id: examId!,
             question_id: qId,
             point: 1 
           })
        ));
      }
      
      // TODO: Add Allowed Students (tương tự add question)
    }

    await getExams(); // Refresh list
    showModal.value = false;
  } catch (err: any) {
    alert('Lỗi: ' + (err.response?.data?.detail || err.message));
  } finally {
    isSubmitting.value = false;
  }
};

// Styles
const getStatusClasses = (status: string) => {
  const colors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-700',
    active: 'bg-green-100 text-green-700',
    ended: 'bg-red-100 text-red-700'
  };
  return colors[status] || '';
};

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    draft: 'Sắp diễn ra',
    active: 'Đang diễn ra',
    ended: 'Đã kết thúc'
  };
  return labels[status] || status;
};
</script>

<template>
  <div>
    <div class="mb-6 flex flex-col sm:flex-row gap-4 justify-between">
      <div class="relative flex-1 max-w-md">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Tìm kiếm đề thi..."
          v-model="searchTerm"
          class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <button
        @click="handleAddExam"
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <Plus class="w-5 h-5" />
        Tạo đề thi mới
      </button>
    </div>

    <div v-if="loading" class="flex justify-center py-10">
      <Loader2 class="w-8 h-8 animate-spin text-blue-600" />
    </div>
    <div v-else-if="error" class="text-center text-red-500 py-10">
      {{ error }}
    </div>

    <div v-else class="space-y-4">
      <div v-for="exam in filteredExams" :key="exam.id" class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-start mb-4">
          <div>
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold">{{ exam.title }}</h3>
              <span 
                :class="`px-3 py-1 rounded-full text-xs font-medium ${getStatusClasses(getExamStatus(exam))}`"
              >
                {{ getStatusLabel(getExamStatus(exam)) }}
              </span>
            </div>
            <div class="text-sm text-gray-600 space-y-1">
              <p>Thời gian: {{ exam.duration_minutes }} phút</p>
              <p>
                Mở: {{ formatDateDisplay(exam.start_time) }} - 
                Đóng: {{ formatDateDisplay(exam.end_time) }}
              </p>
              <p v-if="exam.has_password" class="text-amber-600 flex items-center gap-1 font-medium">
                 Có mật khẩu bảo vệ
              </p>
            </div>
          </div>
          
          <div class="flex gap-2">
            <button @click="handleEditExam(exam)" class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg" title="Sửa">
              <Edit2 class="w-4 h-4" />
            </button>
            <button @click="handleDeleteExam(exam.id)" class="p-2 text-red-600 hover:bg-red-50 rounded-lg" title="Xóa">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <div class="flex items-center gap-2 text-sm border-t pt-3 mt-3">
          <span v-if="exam.show_answers" class="flex items-center gap-2 text-green-600">
            <Eye class="w-4 h-4" /> Xem đáp án: Có
          </span>
          <span v-else class="flex items-center gap-2 text-gray-600">
            <EyeOff class="w-4 h-4" /> Xem đáp án: Không
          </span>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div class="bg-white rounded-lg p-6 w-full max-w-4xl my-8 max-h-[90vh] overflow-y-auto">
        <h2 class="mb-4 text-xl font-bold">
          {{ editingExamId ? 'Sửa đề thi' : 'Tạo đề thi mới' }}
        </h2>
        
        <form @submit.prevent="handleSubmit">
          <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="md:col-span-2">
                <label class="block mb-2 font-medium">Tên đề thi</label>
                <input type="text" v-model="formData.title" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" required />
              </div>
              <div class="md:col-span-2">
                <label class="block mb-2 font-medium">Mô tả</label>
                <textarea v-model="formData.description" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" rows="2"></textarea>
              </div>
              <div>
                <label class="block mb-2 font-medium">Thời gian (phút)</label>
                <input type="number" v-model.number="formData.duration_minutes" class="w-full px-4 py-2 border rounded-lg" min="1" required />
              </div>
              <div>
                <label class="block mb-2 font-medium">Mật khẩu (để trống nếu không đổi)</label>
                <input type="text" v-model="formData.password" class="w-full px-4 py-2 border rounded-lg" placeholder="***" />
              </div>
              <div>
                <label class="block mb-2 font-medium">Bắt đầu</label>
                <input type="datetime-local" v-model="formData.start_time" class="w-full px-4 py-2 border rounded-lg" required />
              </div>
              <div>
                <label class="block mb-2 font-medium">Kết thúc</label>
                <input type="datetime-local" v-model="formData.end_time" class="w-full px-4 py-2 border rounded-lg" required />
              </div>
              <div class="md:col-span-2">
                <label class="flex items-center gap-2">
                  <input type="checkbox" v-model="formData.show_answers" class="w-4 h-4" />
                  Cho phép xem đáp án sau khi thi
                </label>
              </div>
            </div>

            <div>
              <label class="block mb-2 font-medium">Chọn câu hỏi ({{ formData.questions.length }} đã chọn)</label>
              
              <div v-if="isLoadingResources" class="text-sm text-gray-500">Đang tải danh sách câu hỏi...</div>
              
              <div v-else class="max-h-60 overflow-y-auto border rounded-lg p-4 space-y-2">
                <label v-for="(q, idx) in availableQuestions" :key="q.id" class="flex items-start gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="formData.questions" 
                    :value="q.id" 
                    class="mt-1"
                  />
                  <div class="text-sm">
                    <span class="font-bold text-gray-600">#{{ q.id }}</span> {{ q.content }}
                  </div>
                </label>
                
                <div v-if="availableQuestions.length === 0" class="text-center text-gray-500 text-sm">
                  Chưa có câu hỏi nào trong ngân hàng đề.
                </div>
              </div>
            </div>

            <div>
              <label class="block mb-2 font-medium">Chọn thí sinh ({{ formData.allowedStudents.length }} đã chọn)</label>
              
              <div v-if="isLoadingResources" class="text-sm text-gray-500">Đang tải danh sách sinh viên...</div>
              
              <div v-else class="max-h-60 overflow-y-auto border rounded-lg p-4 space-y-2">
                <label v-for="std in availableStudents" :key="std.id" class="flex items-center gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="formData.allowedStudents" 
                    :value="std.id" 
                  />
                  <div class="text-sm">
                    <p class="font-medium">{{ std.full_name }}</p>
                    <p class="text-gray-500 text-xs">{{ std.code }}</p>
                  </div>
                </label>
                 <div v-if="availableStudents.length === 0" class="text-center text-gray-500 text-sm">
                  Không tìm thấy sinh viên nào.
                </div>
              </div>
            </div>
          </div>
          
          <div class="flex gap-3 mt-6">
            <button type="button" @click="showModal = false" class="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50">
              Hủy
            </button>
            <button type="submit" :disabled="isSubmitting" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              <span v-if="isSubmitting"><Loader2 class="w-4 h-4 animate-spin inline mr-2"/>Đang xử lý...</span>
              <span v-else>{{ editingExamId ? 'Cập nhật' : 'Tạo đề thi' }}</span>
            </button>
          </div>
        </form> 
      </div>
    </div>
  </div>
</template>