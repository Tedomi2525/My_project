// types/index.ts
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
  // password: string;
  fullName: string;
  email?: string;
  role: 'admin' | 'teacher' | 'student';
  studentId?: string;
}

export interface Question {
  id: string;
  content: string;
  imageUrl?: string;
  options: string[];
  correctAnswer: number;
  createdBy: string;
  createdAt: Date;
}

export interface Exam {
  id: string;
  title: string;
  duration: number; // minutes
  startTime: Date | string; // Cho phép string để tương thích input date
  endTime: Date | string;
  questions: string[]; // question IDs
  allowedStudents: string[]; // student IDs
  status: 'draft' | 'active' | 'ended';
  showAnswers: boolean;
  createdBy: string;
  password?: string;
}

export interface ExamResult {
  id: string;
  examId: string;
  studentId: string;
  answers: number[]; // indices of selected answers
  score: number;
  submittedAt: Date;
}

export interface StudentInClass {
  id: number
  full_name: string
  email: string
  student_code?: string
  joined_at: string
}

export interface Class {
  id: number
  name: string
  description?: string
  teacher_id: number
  students: StudentInClass[]
  student_count: number
}

export interface AvailableStudent {
  id: number
  full_name: string
  student_code?: string
} 
