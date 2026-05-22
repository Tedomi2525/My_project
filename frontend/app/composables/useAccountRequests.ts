export interface AccountRequest {
  id: number
  full_name: string
  email?: string | null
  role: 'teacher' | 'student'
  note?: string | null
  status: 'pending' | 'approved' | 'rejected'
  email_status: 'pending' | 'sent' | 'failed'
  email_error?: string | null
  email_sent_at?: string | null
  created_account_id?: number | null
  created_at: string
  updated_at: string
}

export interface AccountRequestStatus {
  id: number
  status: 'pending' | 'approved' | 'rejected'
  role: 'teacher' | 'student'
  username?: string | null
  password?: string | null
  message: string
}

export const useAccountRequests = () => {
  const config = useRuntimeConfig()
  const API_BASE = config.public.apiBase
  const token = useCookie<string | null>('token')

  const api = <T>(url: string, options: any = {}) => {
    return $fetch<T>(url, {
      baseURL: API_BASE,
      headers: token.value ? { Authorization: `Bearer ${token.value}` } : {},
      ...options
    })
  }

  const createAccountRequest = (payload: {
    full_name: string
    email?: string
    role: 'teacher' | 'student'
    note?: string
  }) => {
    return api<AccountRequest>('/account-requests/', {
      method: 'POST',
      body: payload
    })
  }

  const getAccountRequests = (status?: string) => {
    const query = status ? `?status=${status}` : ''
    return api<AccountRequest[]>(`/account-requests/${query}`)
  }

  const approveAccountRequest = (id: number) => {
    return api<AccountRequest>(`/account-requests/${id}/approve`, { method: 'POST' })
  }

  const rejectAccountRequest = (id: number) => {
    return api<AccountRequest>(`/account-requests/${id}/reject`, { method: 'POST' })
  }

  const getAccountRequestStatus = (id: number) => {
    return api<AccountRequestStatus>(`/account-requests/${id}/status`)
  }

  return {
    createAccountRequest,
    getAccountRequests,
    approveAccountRequest,
    rejectAccountRequest,
    getAccountRequestStatus
  }
}
