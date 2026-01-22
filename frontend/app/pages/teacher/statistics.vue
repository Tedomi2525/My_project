<script setup lang="ts">
import { ref, computed } from 'vue';
import { Download, Eye } from 'lucide-vue-next';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement
} from 'chart.js';
import { Bar, Pie } from 'vue-chartjs';

// --- Đăng ký các thành phần của Chart.js ---
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

definePageMeta({
  layout: 'teacher'
});


// --- Interfaces & Mock Data ---
interface ExamResult {
  id: string;
  examId: string;
  studentId: string;
  answers: number[];
  score: number;
  submittedAt: Date;
}

const props = defineProps<{
  teacherId?: string; // Optional prop để tránh lỗi nếu không truyền
}>();

const mockExams = [
  { id: 'exam1', title: 'Kiểm tra giữa kỳ - Lập trình Web' },
  { id: 'exam2', title: 'Bài tập tuần 5' }
];

const mockResults: ExamResult[] = [
  {
    id: 'result1',
    examId: 'exam1',
    studentId: 'student1',
    answers: [0, 2],
    score: 5,
    submittedAt: new Date('2024-02-01T08:30:00')
  },
  {
    id: 'result2',
    examId: 'exam1',
    studentId: 'student2',
    answers: [0, 2],
    score: 10,
    submittedAt: new Date('2024-02-01T08:45:00')
  },
  {
    id: 'result3',
    examId: 'exam1',
    studentId: 'student3',
    answers: [1, 1],
    score: 2.5,
    submittedAt: new Date('2024-02-01T09:00:00')
  }
];

const mockStudents = [
  { id: 'student1', name: 'Lê Văn Minh', studentId: 'SV001' },
  { id: 'student2', name: 'Nguyễn Thị Hương', studentId: 'SV002' },
  { id: 'student3', name: 'Hoàng Minh Tuấn', studentId: 'SV003' }
];

const mockQuestions = [
  {
    id: 'q1',
    content: 'HTML là viết tắt của gì?',
    options: [
      'Hyper Text Markup Language',
      'High Tech Modern Language',
      'Home Tool Markup Language',
      'Hyperlinks and Text Markup Language'
    ],
    correctAnswer: 0
  },
  {
    id: 'q2',
    content: 'CSS được sử dụng để làm gì?',
    options: [
      'Tạo cấu trúc trang web',
      'Tạo hiệu ứng động',
      'Tạo kiểu dáng cho trang web',
      'Lưu trữ dữ liệu'
    ],
    correctAnswer: 2
  }
];

// --- State Management ---
const selectedExam = ref('exam1');
const showAnswersModal = ref(false);
const selectedResult = ref<ExamResult | null>(null);

// --- Computed Statistics ---
const examResults = computed(() => mockResults.filter(r => r.examId === selectedExam.value));

const avgScore = computed(() => {
  if (examResults.value.length === 0) return '0';
  const sum = examResults.value.reduce((acc, r) => acc + r.score, 0);
  return (sum / examResults.value.length).toFixed(2);
});

const maxScore = computed(() => 
  examResults.value.length > 0 ? Math.max(...examResults.value.map(r => r.score)) : 0
);

const minScore = computed(() => 
  examResults.value.length > 0 ? Math.min(...examResults.value.map(r => r.score)) : 0
);

// --- Chart Data Configuration ---

// 1. Bar Chart Data (Phổ điểm)
const barChartData = computed(() => {
  const distribution = [
    { range: '0-2', count: examResults.value.filter(r => r.score < 3).length },
    { range: '3-4', count: examResults.value.filter(r => r.score >= 3 && r.score < 5).length },
    { range: '5-6', count: examResults.value.filter(r => r.score >= 5 && r.score < 7).length },
    { range: '7-8', count: examResults.value.filter(r => r.score >= 7 && r.score < 9).length },
    { range: '9-10', count: examResults.value.filter(r => r.score >= 9).length }
  ];

  return {
    labels: distribution.map(d => d.range),
    datasets: [{
      label: 'Số sinh viên',
      data: distribution.map(d => d.count),
      backgroundColor: '#3b82f6',
    }]
  };
});

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
};

// 2. Pie Chart Data (Phân loại)
const pieChartData = computed(() => {
  const distribution = [
    { name: 'Giỏi (8-10)', value: examResults.value.filter(r => r.score >= 8).length, color: '#22c55e' },
    { name: 'Khá (6.5-8)', value: examResults.value.filter(r => r.score >= 6.5 && r.score < 8).length, color: '#3b82f6' },
    { name: 'TB (5-6.5)', value: examResults.value.filter(r => r.score >= 5 && r.score < 6.5).length, color: '#f59e0b' },
    { name: 'Yếu (<5)', value: examResults.value.filter(r => r.score < 5).length, color: '#ef4444' }
  ];

  return {
    labels: distribution.map(d => d.name),
    datasets: [{
      data: distribution.map(d => d.value),
      backgroundColor: distribution.map(d => d.color),
    }]
  };
});

const pieChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
};

// --- Methods ---
const handleViewAnswers = (result: ExamResult) => {
  selectedResult.value = result;
  showAnswersModal.value = true;
};

const handleExportExcel = () => {
  const csv = examResults.value.map(result => {
    const student = mockStudents.find(s => s.id === result.studentId);
    return `${student?.studentId},${student?.name},${result.score},${result.submittedAt.toLocaleString('vi-VN')}`;
  }).join('\n');
  
  const blob = new Blob([`Mã SV,Họ tên,Điểm,Thời gian nộp\n${csv}`], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'bang_diem.csv';
  a.click();
};

const getScoreColorClass = (score: number) => {
  if (score >= 8) return 'bg-green-100 text-green-700';
  if (score >= 6.5) return 'bg-blue-100 text-blue-700';
  if (score >= 5) return 'bg-yellow-100 text-yellow-700';
  return 'bg-red-100 text-red-700';
};
</script>

<template>
  <div>
    <div className="mb-6 bg-white rounded-lg shadow p-6">
      <label className="block mb-2 font-medium">Chọn đề thi</label>
      <select
        v-model="selectedExam"
        className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option v-for="exam in mockExams" :key="exam.id" :value="exam.id">
          {{ exam.title }}
        </option>
      </select>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600 mb-2">Số thí sinh</p>
        <p className="text-3xl font-bold">{{ examResults.length }}</p>
      </div>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600 mb-2">Điểm trung bình</p>
        <p className="text-3xl font-bold text-blue-600">{{ avgScore }}</p>
      </div>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600 mb-2">Điểm cao nhất</p>
        <p className="text-3xl font-bold text-green-600">{{ maxScore }}</p>
      </div>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600 mb-2">Điểm thấp nhất</p>
        <p className="text-3xl font-bold text-red-600">{{ minScore }}</p>
      </div>
    </div>

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="mb-4 font-bold text-lg">Phổ điểm</h3>
        <div className="h-75">
          <Bar :data="barChartData" :options="barChartOptions" />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="mb-4 font-bold text-lg">Phân loại học lực</h3>
        <div className="h-75">
          <Pie :data="pieChartData" :options="pieChartOptions" />
        </div>
      </div>
    </div>

    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-6 border-b border-gray-200 flex justify-between items-center">
        <h3 className="font-bold text-lg">Bảng điểm chi tiết</h3>
        <button
          @click="handleExportExcel"
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          <Download className="w-5 h-5" />
          Xuất Excel
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left">STT</th>
              <th className="px-6 py-3 text-left">Mã SV</th>
              <th className="px-6 py-3 text-left">Họ tên</th>
              <th className="px-6 py-3 text-left">Điểm</th>
              <th className="px-6 py-3 text-left">Thời gian nộp</th>
              <th className="px-6 py-3 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            <tr v-for="(result, idx) in examResults" :key="result.id" className="hover:bg-gray-50">
              <td className="px-6 py-4">{{ idx + 1 }}</td>
              <td className="px-6 py-4">
                {{ mockStudents.find(s => s.id === result.studentId)?.studentId }}
              </td>
              <td className="px-6 py-4">
                {{ mockStudents.find(s => s.id === result.studentId)?.name }}
              </td>
              <td className="px-6 py-4">
                <span :className="`px-3 py-1 rounded-full text-sm ${getScoreColorClass(result.score)}`">
                  {{ result.score }}
                </span>
              </td>
              <td className="px-6 py-4">
                {{ result.submittedAt.toLocaleString('vi-VN') }}
              </td>
              <td className="px-6 py-4">
                <div className="flex gap-2 justify-end">
                  <button
                    @click="handleViewAnswers(result)"
                    className="flex items-center gap-2 px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    Xem đáp án
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showAnswersModal && selectedResult" className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[80vh] overflow-y-auto">
        <h2 className="mb-4 text-xl font-bold">
          Chi tiết bài làm - {{ mockStudents.find(s => s.id === selectedResult?.studentId)?.name }}
        </h2>
        <div className="space-y-6">
          <div v-for="(question, idx) in mockQuestions" :key="question.id" className="border-b border-gray-200 pb-4">
            <p className="mb-3">
              <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm mr-2">
                Câu {{ idx + 1 }}
              </span>
              {{ question.content }}
            </p>
            <div className="ml-4 space-y-2">
              <div
                v-for="(option, optIdx) in question.options"
                :key="optIdx"
                :class="[
                  'p-3 rounded-lg border',
                  optIdx === question.correctAnswer 
                    ? 'bg-green-50 border-green-200' 
                    : optIdx === selectedResult.answers[idx] && optIdx !== question.correctAnswer
                      ? 'bg-red-50 border-red-200'
                      : 'bg-gray-50 border-transparent'
                ]"
              >
                <span className="text-gray-600 mr-2">{{ String.fromCharCode(65 + optIdx) }}.</span>
                {{ option }}
                <span v-if="optIdx === question.correctAnswer" className="ml-2 text-green-600 font-medium">
                  (Đáp án đúng)
                </span>
                <span v-if="optIdx === selectedResult.answers[idx] && optIdx !== question.correctAnswer" className="ml-2 text-red-600">
                  (Đã chọn)
                </span>
                <span v-if="optIdx === selectedResult.answers[idx] && optIdx === question.correctAnswer" className="ml-2 text-green-600">
                  (Đã chọn đúng)
                </span>
              </div>
            </div>
          </div>
        </div>
        <button
          @click="showAnswersModal = false"
          className="w-full mt-6 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Đóng
        </button>
      </div>
    </div>
  </div>
</template>