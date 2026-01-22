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

// ~/types/index.ts
export interface Question {
  id: number
  content: string
  question_type: string
  difficulty: 'EASY' | 'MEDIUM' | 'HARD' 
  options: Record<string, string> | null
  correct_answer: string
  created_by: number
}


export interface Exam {
  id: number;
  title: string;
  description?: string | null;
  duration_minutes: number;
  start_time: string | null;
  end_time: string | null;
  show_answers: boolean;
  created_by: number;
  has_password: boolean;
  questions?: number[];
  allowed_students?: number[];
  status?: 'draft' | 'active' | 'ended';
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
