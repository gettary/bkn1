import api from './api'

export const authService = {
  async login(username, password) {
    const response = await api.post('/auth/login', { username, password })
    return response.data
  },

  async getProfile() {
    const response = await api.get('/auth/profile')
    return response.data
  },

  async getUsers() {
    const response = await api.get('/auth/users')
    return response.data
  },

  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}

export const assessmentService = {
  async getAssessments() {
    const response = await api.get('/assessments')
    return response.data
  },

  async getAssessment(id) {
    const response = await api.get(`/assessments/${id}`)
    return response.data
  },

  async createAssessment(assessment) {
    const response = await api.post('/assessments', assessment)
    return response.data
  },

  async updateAssessment(id, assessment) {
    const response = await api.put(`/assessments/${id}`, assessment)
    return response.data
  },

  async deleteAssessment(id) {
    const response = await api.delete(`/assessments/${id}`)
    return response.data
  },

  async publishAssessment(id) {
    const response = await api.put(`/assessments/${id}`, { status: 'published' })
    return response.data
  }
}

export const userDataService = {
  async getUserData(indicatorItemId) {
    const response = await api.get(`/user-data/${indicatorItemId}`)
    return response.data
  },

  async saveUserData(indicatorItemId, data) {
    const response = await api.post(`/user-data/${indicatorItemId}`, data)
    return response.data
  },

  async uploadImage(indicatorItemId, file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post(`/user-data/${indicatorItemId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async getAssessmentReport(assessmentId) {
    const response = await api.get(`/user-data/report/${assessmentId}`)
    return response.data
  },

  async deleteUploadedFile(indicatorItemId) {
    const response = await api.delete(`/user-data/${indicatorItemId}/delete`)
    return response.data
  }
}

