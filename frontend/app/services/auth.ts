import type { LoginCredentials } from '~/types' // Giả sử bạn đã có type này cho user/pass

// 1. Định nghĩa Interface phản hồi từ Backend (Python FastAPI thường trả về snake_case)
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  full_name: string;
  email: string | null;
  role: 'admin' | 'teacher' | 'student';
  student_id: string | null;
}

export const authService = {
  // 2. Gán kiểu Promise<AuthResponse> cho hàm login
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // 3. Truyền Generic vào $fetch để ép kiểu kết quả trả về
    return await $fetch<AuthResponse>('http://localhost:8000/login', { 
      method: 'POST',
      body: credentials
    })
  }
}