// utils/common.ts

/**
 * Shared utility functions
 */

export function handleApiError(error: any, context: string = 'API call') {
  console.error(`❌ ${context} failed:`, error)
  
  if (error && error.name === 'TypeError' && error.message && error.message.includes('fetch')) {
    return 'Không thể kết nối đến server backend. Vui lòng kiểm tra server Python có đang chạy không.'
  }
  
  return error?.message || 'Có lỗi không xác định xảy ra'
}

// Sửa lại apiCall để tự động ghép link Backend
export async function apiCall(endpoint: string, options: RequestInit = {}) {
  const config = useRuntimeConfig()
  // Tự động thêm dấu / nếu thiếu
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  const url = `${config.public.apiBase}${path}`

  try {
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        ...options.headers // Cho phép ghi đè header nếu cần (ví dụ Authorization)
      },
      ...options
    })

    if (!response.ok) {
      // Logic xử lý lỗi chuẩn của FastAPI
      const errorData = await response.json().catch(() => null)
      const errorMessage = Array.isArray(errorData?.detail) 
        ? errorData.detail.map((err: any) => err.msg).join(', ')
        : errorData?.detail || `HTTP ${response.status}: ${response.statusText}`
      
      throw new Error(errorMessage)
    }

    return await response.json()
  } catch (error) {
    throw new Error(handleApiError(error))
  }
}

// ... (Các hàm showNotification, confirmAction, transformCourseData giữ nguyên)
export function showNotification(message: string, type: 'success' | 'error' = 'success') {
  if (import.meta.client) {
    const prefix = type === 'success' ? '✅' : '❌'
    alert(`${prefix} ${message}`)
  }
}

export function confirmAction(message: string): boolean {
  if (import.meta.client) {
    return confirm(message)
  }
  return false
}
