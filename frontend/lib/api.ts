import axios from 'axios'

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minute timeout for roadmap generation and quarterly reports
})

// Add error interceptor - silent mode (don't log errors to console)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Silently handle errors - don't log to console
    // Errors are handled by components using cached data
    return Promise.reject(error)
  }
)

export default api

export const dashboardApi = {
  getOverview: () => api.get('/api/dashboard/overview'),
  getInsights: () => api.get('/api/dashboard/insights'),
  getRecommendations: (status?: string, quarter?: string, year?: number) => 
    api.get('/api/dashboard/recommendations', { params: { status, quarter, year } }),
  getRoadmaps: () => api.get('/api/dashboard/roadmaps'),
  clearDatabase: () => api.post('/api/dashboard/clear-database'),
}

export const roadmapApi = {
  generate: (data: any) => api.post('/api/roadmap/generate', data, { timeout: 300000 }), // 5 minutes for roadmap generation
  getOnePager: (id: number) => api.get(`/api/roadmap/one-pager/${id}`),
}

export const quarterlyReportsApi = {
  getReport: (quarter: string, year: number) => api.get(`/api/quarterly-reports/${quarter}/${year}`, { timeout: 120000 }).catch(() => { throw new Error('Network error') }), // 2 minutes for quarterly reports
  getCurrent: () => api.get('/api/quarterly-reports/current', { timeout: 120000 }).catch(() => { throw new Error('Network error') }),
  listAvailable: () => api.get('/api/quarterly-reports/').catch(() => { throw new Error('Network error') }),
}

export const feedbackApi = {
  list: (params?: any) => api.get('/api/feedback', { params }),
  getThemes: (limit?: number, quarter?: string, year?: number) => 
    api.get('/api/feedback/themes', { params: { limit, quarter, year } }),
  getTheme: (id: number) => api.get(`/api/feedback/themes/${id}`),
  process: (data: any) => api.post('/api/feedback/process', data),
}

export const competitorApi = {
  list: () => api.get('/api/competitor'),
  get: (id: number) => api.get(`/api/competitor/${id}`),
  analyze: (data: any) => api.post('/api/competitor/analyze', data),
}

export const documentApi = {
  list: () => api.get('/api/documents'),
  get: (id: number) => api.get(`/api/documents/${id}`),
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/api/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export const agentsApi = {
  analyze: (data: any) => api.post('/api/agents/analyze', data),
  getStatus: () => api.get('/api/agents/status'),
}

export const recommendationsApi = {
  updateStatus: (id: number, status: string, shippedAt?: string) => 
    api.patch(`/api/recommendations/${id}/status`, { status, shipped_at: shippedAt }),
}

export const customerNotificationsApi = {
  notify: (recommendationId: number) => 
    api.post(`/api/customer-notifications/notify/${recommendationId}`),
  getCustomers: (recommendationId: number) => 
    api.get(`/api/customer-notifications/customers/${recommendationId}`),
}

export const adoptionApi = {
  getAdoptionStats: (recommendationId: number) => 
    api.get(`/api/adoption/${recommendationId}`),
  trackAdoption: (recommendationId: number, customerId: string, adopted: boolean) => 
    api.post(`/api/adoption/track`, { recommendation_id: recommendationId, customer_id: customerId, adopted }),
}

export const feedbackLoopApi = {
  notifyCustomers: (recommendationId: number, generateEmails: boolean = true) =>
    api.post(`/api/feedback-loop/notify/${recommendationId}`, { generate_emails: generateEmails }),
  getEmailTemplate: (recommendationId: number, customerId: string) =>
    api.get(`/api/feedback-loop/email-template/${recommendationId}/${customerId}`),
  getAdoptionStats: (recommendationId: number) =>
    api.get(`/api/feedback-loop/adoption-stats/${recommendationId}`),
}

export const n8nTriggerApi = {
  triggerWorkflow: (data?: { cached_data?: any[] }) => api.post('/api/n8n/trigger-workflow', data || {}),
  getWorkflowStatus: () => api.get('/api/n8n/workflow-status'),
}

