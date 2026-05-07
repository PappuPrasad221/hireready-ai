import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const isFormData = options.body instanceof FormData
    const headers = {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...options.headers,
    }

    const config = {
      url,
      method: options.method || 'GET',
      headers: {
        ...headers,
      },
      data: options.body,
    }

    try {
      const response = await axios(config)
      return response.data
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Resume API
  async uploadResume(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    return this.request('/api/resume/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // Remove content-type to let browser set it for FormData
    })
  }

  async getResumeAnalysis(resumeId) {
    return this.request(`/api/resume/analysis/${resumeId}`)
  }

  async extractSkills(text) {
    return this.request('/api/resume/extract-skills', {
      method: 'POST',
      body: JSON.stringify({ text }),
    })
  }

  // Job API
  async getJobInsights(company, role, location) {
    return this.request('/api/job/insights', {
      method: 'POST',
      body: JSON.stringify({ company, role, location }),
    })
  }

  async searchJobs(query, location, limit = 10) {
    return this.request('/api/job/search', {
      method: 'POST',
      body: JSON.stringify({ query, location, limit }),
    })
  }

  async getPopularRoles() {
    return this.request('/api/job/popular-roles')
  }

  async getPopularCompanies() {
    return this.request('/api/job/popular-companies')
  }

  async getSkillsForRole(role) {
    return this.request(`/api/job/skills-for-role/${role}`)
  }

  async getSalaryEstimate(company, role, location) {
    return this.request('/api/job/salary-estimate', {
      method: 'POST',
      body: JSON.stringify({ company, role, location }),
    })
  }

  // Interview API
  async generateInterviewQuestions(request) {
    return this.request('/api/interview/start', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async evaluateAnswer(evaluation) {
    return this.request('/api/interview/evaluate', {
      method: 'POST',
      body: JSON.stringify(evaluation),
    })
  }

  async generateFollowupQuestion(evaluation) {
    return this.request('/api/interview/followup', {
      method: 'POST',
      body: JSON.stringify(evaluation),
    })
  }

  async startInterviewSession(request) {
    return this.request('/api/interview/start-session', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async endInterviewSession(session) {
    return this.request('/api/report/generate', {
      method: 'POST',
      body: JSON.stringify(session),
    })
  }

  async getSessionData(sessionId) {
    return this.request(`/api/interview/session/${sessionId}`)
  }

  async trackBehavior(behaviorData) {
    return this.request('/api/interview/track-behavior', {
      method: 'POST',
      body: JSON.stringify(behaviorData),
    })
  }

  // Analytics API
  async getDashboardAnalytics(userId, period = 'week') {
    return this.request('/api/analytics/dashboard', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, period }),
    })
  }

  async getPerformanceTrends(userId, period = 'week') {
    return this.request('/api/analytics/performance-trends', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, period }),
    })
  }

  async getSkillsBreakdown(userId, period = 'week') {
    return this.request('/api/analytics/skills-breakdown', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, period }),
    })
  }

  async getPeerComparison(userId) {
    return this.request('/api/analytics/comparison', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    })
  }

  async recordPerformance(metrics) {
    return this.request('/api/analytics/record-performance', {
      method: 'POST',
      body: JSON.stringify(metrics),
    })
  }

  async getLeaderboard(limit = 10, timePeriod = 'week') {
    return this.request(`/api/analytics/leaderboard?limit=${limit}&time_period=${timePeriod}`)
  }

  async getUserStatistics(userId) {
    return this.request(`/api/analytics/user-stats/${userId}`)
  }

  async exportUserData(userId, period = 'all') {
    return this.request('/api/analytics/export-data', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, period }),
    })
  }
}

export const apiService = new ApiService()
export default apiService
