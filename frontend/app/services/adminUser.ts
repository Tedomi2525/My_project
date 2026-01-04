export const adminUserService = {
  getAll() {
    return $fetch('/admin/users', {
      baseURL: 'http://localhost:8000',
      headers: {
        Authorization: `Bearer ${useCookie('token').value}`
      }
    })
  },

  create(data: any) {
    return $fetch('/admin/users', {
      method: 'POST',
      baseURL: 'http://localhost:8000',
      headers: {
        Authorization: `Bearer ${useCookie('token').value}`
      },
      body: data
    })
  },

  update(id: string, data: any) {
    return $fetch(`/admin/users/${id}`, {
      method: 'PUT',
      baseURL: 'http://localhost:8000',
      headers: {
        Authorization: `Bearer ${useCookie('token').value}`
      },
      body: data
    })
  },

  remove(id: string) {
    return $fetch(`/admin/users/${id}`, {
      method: 'DELETE',
      baseURL: 'http://localhost:8000',
      headers: {
        Authorization: `Bearer ${useCookie('token').value}`
      }
    })
  },

  resetPassword(id: string) {
    return $fetch(`/admin/users/${id}/reset-password`, {
      method: 'POST',
      baseURL: 'http://localhost:8000',
      headers: {
        Authorization: `Bearer ${useCookie('token').value}`
      }
    })
  }
}
