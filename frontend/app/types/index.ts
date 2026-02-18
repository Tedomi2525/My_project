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
  // show_answers: boolean;
  allow_view_answers?: boolean;
  created_by: number;
  has_password: boolean;
  allowed_classes: number[]; 
  exam_questions: number[];
  status?: 'draft' | 'active' | 'ended';
}
export interface ExamResult {
  id: number;
  exam_id: number;
  student_id: number;
  total_score: number;
  started_at: string | null;
  finished_at: string | null;
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
