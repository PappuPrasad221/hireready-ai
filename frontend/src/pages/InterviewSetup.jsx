import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import { Briefcase, MapPin, Building, Users, TrendingUp, Target, Clock, DollarSign, ArrowRight, Search, Sparkles } from 'lucide-react'
import apiService from '../api/api'

const InterviewSetup = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    company: '',
    role: '',
    location: ''
  })
  const [jobInsights, setJobInsights] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const getSkills = (insights) => insights?.skills || insights?.requiredSkills || []
  const getRequirements = (insights) => insights?.requirements || insights?.companySpecificExpectations || []
  const getSalary = (insights) => insights?.salary || insights?.salary_range || insights?.salaryRange || 'Not available'
  const getCompetition = (insights) => {
    if (!insights?.confidence && insights?.confidence !== 0) return 'Not available'
    return `${Math.round(insights.confidence)}% insight confidence`
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const fetchJobInsights = async () => {
    if (!formData.role || !formData.company) {
      alert('Please fill in company and role fields')
      return
    }

    setIsLoading(true)

    try {
      const response = await apiService.getJobInsights(formData.company, formData.role, formData.location)
      const insights = response.insights || {}
      setJobInsights(insights)
      sessionStorage.setItem('jobInsights', JSON.stringify(insights))
      sessionStorage.setItem('targetPosition', JSON.stringify(formData))
    } catch (error) {
      console.error('Job insights failed:', error)
      alert('Unable to fetch job insights. Please make sure the backend is running and try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const generateInterview = async () => {
    if (!formData.company || !formData.role || !formData.location) {
      alert('Please fill in all fields')
      return
    }
    setIsLoading(true)

    try {
      const resumeData = JSON.parse(sessionStorage.getItem('resumeAnalysis') || '{}')
      const insights = jobInsights || JSON.parse(sessionStorage.getItem('jobInsights') || '{}')
      const response = await apiService.generateInterviewQuestions({
        ...formData,
        resume_data: resumeData,
        job_insights: insights
      })

      const questions = response.session?.questions || response.questions || []
      const interviewState = {
        ...formData,
        resumeData,
        jobInsights: insights,
        questions,
        sessionId: response.session?.session_id || response.session_id
      }

      sessionStorage.setItem('interviewState', JSON.stringify(interviewState))
      navigate('/interview', { state: interviewState })
    } catch (error) {
      console.error('Question generation failed:', error)
      alert('Unable to generate interview questions. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const popularRoles = [
    'Software Engineer',
    'Product Manager',
    'Data Scientist',
    'UX Designer',
    'DevOps Engineer',
    'Frontend Developer',
    'Backend Developer',
    'Full Stack Developer'
  ]

  const popularCompanies = [
    'Google',
    'Microsoft',
    'Amazon',
    'Apple',
    'Meta',
    'Netflix',
    'Tesla',
    'Spotify'
  ]

  return (
    <div className="min-h-screen relative">
      {/* Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-dark-bg via-dark-surface to-dark-bg">
        <div className="absolute inset-0 opacity-20">
          {[...Array(15)].map((_, i) => (
            <div
              key={i}
              className="absolute rounded-full bg-neon-purple opacity-10 animate-pulse-slow"
              style={{
                width: Math.random() * 80 + 40 + 'px',
                height: Math.random() * 80 + 40 + 'px',
                left: Math.random() * 100 + '%',
                top: Math.random() * 100 + '%',
                animationDelay: Math.random() * 5 + 's',
                animationDuration: Math.random() * 8 + 8 + 's'
              }}
            />
          ))}
        </div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 glass-card mx-4 mt-4 px-8 py-4 rounded-2xl">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Briefcase className="w-8 h-8 text-neon-blue" />
            <span className="text-2xl font-bold text-gradient">Interview Setup</span>
          </div>
          <Link to="/resume" className="text-gray-300 hover:text-white transition-colors">← Back</Link>
        </div>
      </nav>

      {/* Main Content */}
      <div className="relative z-10 container mx-auto px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-6xl mx-auto"
        >
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-gradient mb-6">
              Configure Your Interview
            </h1>
            <p className="text-xl text-gray-300">
              Set up your target role and get AI-powered insights for personalized preparation
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left Panel - Form */}
            <motion.div
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <div className="glass-card p-8 rounded-3xl">
                <h2 className="text-2xl font-semibold mb-6 flex items-center">
                  <Target className="w-6 h-6 mr-3 text-neon-cyan" />
                  Target Position
                </h2>

                <div className="space-y-6">
                  {/* Company Input */}
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">
                      Company
                    </label>
                    <div className="relative">
                      <Building className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="text"
                        name="company"
                        value={formData.company}
                        onChange={handleInputChange}
                        placeholder="e.g., Google, Microsoft, Startup"
                        className="input-field pl-12 w-full"
                      />
                    </div>
                    {/* Popular Companies */}
                    <div className="mt-3 flex flex-wrap gap-2">
                      {popularCompanies.slice(0, 4).map((company) => (
                        <button
                          key={company}
                          onClick={() => setFormData(prev => ({ ...prev, company }))}
                          className="px-3 py-1 rounded-full bg-glass-border text-xs hover:bg-neon-blue/20 transition-colors"
                        >
                          {company}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Role Input */}
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">
                      Role
                    </label>
                    <div className="relative">
                      <Briefcase className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="text"
                        name="role"
                        value={formData.role}
                        onChange={handleInputChange}
                        placeholder="e.g., Software Engineer, Product Manager"
                        className="input-field pl-12 w-full"
                      />
                    </div>
                    {/* Popular Roles */}
                    <div className="mt-3 flex flex-wrap gap-2">
                      {popularRoles.slice(0, 4).map((role) => (
                        <button
                          key={role}
                          onClick={() => setFormData(prev => ({ ...prev, role }))}
                          className="px-3 py-1 rounded-full bg-glass-border text-xs hover:bg-neon-blue/20 transition-colors"
                        >
                          {role}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Location Input */}
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">
                      Location
                    </label>
                    <div className="relative">
                      <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="text"
                        name="location"
                        value={formData.location}
                        onChange={handleInputChange}
                        placeholder="e.g., San Francisco, Remote, New York"
                        className="input-field pl-12 w-full"
                      />
                    </div>
                  </div>

                  {/* Get Insights Button */}
                  <button
                    onClick={fetchJobInsights}
                    disabled={isLoading}
                    className="w-full btn-secondary flex items-center justify-center"
                  >
                    {isLoading ? (
                      <>
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                          className="mr-2"
                        >
                          <Sparkles className="w-5 h-5" />
                        </motion.div>
                        Fetching Insights...
                      </>
                    ) : (
                      <>
                        <Search className="w-5 h-5 mr-2" />
                        Get Job Insights
                      </>
                    )}
                  </button>
                </div>
              </div>
            </motion.div>

            {/* Right Panel - Job Insights */}
            <motion.div
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              {jobInsights ? (
                <div className="space-y-6">
                  {jobInsights.confidenceWarning && (
                    <div className="glass-card p-4 rounded-xl border-yellow-400/40 bg-yellow-500/10 text-yellow-200">
                      {jobInsights.warningMessage || 'Please paste job description for better accuracy.'}
                    </div>
                  )}
                  {/* Skills Required */}
                  <div className="glass-card p-6 rounded-2xl">
                    <h3 className="text-xl font-semibold mb-4 flex items-center">
                      <TrendingUp className="w-5 h-5 mr-2 text-neon-cyan" />
                      Key Skills Required
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {getSkills(jobInsights).map((skill, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 rounded-full bg-neon-purple/20 text-neon-cyan text-sm border border-neon-purple/30"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Responsibilities */}
                  <div className="glass-card p-6 rounded-2xl">
                    <h3 className="text-xl font-semibold mb-4 flex items-center">
                      <Users className="w-5 h-5 mr-2 text-neon-cyan" />
                      Key Responsibilities
                    </h3>
                    <ul className="space-y-2">
                      {(jobInsights.responsibilities || []).map((resp, index) => (
                        <li key={index} className="text-gray-300 text-sm flex items-start">
                          <span className="text-neon-blue mr-2">•</span>
                          {resp}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Requirements */}
                  <div className="glass-card p-6 rounded-2xl">
                    <h3 className="text-xl font-semibold mb-4 flex items-center">
                      <Target className="w-5 h-5 mr-2 text-neon-cyan" />
                      Requirements
                    </h3>
                    <ul className="space-y-2">
                      {getRequirements(jobInsights).map((req, index) => (
                        <li key={index} className="text-gray-300 text-sm flex items-start">
                          <span className="text-neon-blue mr-2">•</span>
                          {req}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Additional Info */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="glass-card p-4 rounded-xl">
                      <div className="flex items-center mb-2">
                        <DollarSign className="w-4 h-4 mr-2 text-green-400" />
                        <span className="text-sm text-gray-400">Salary Range</span>
                      </div>
                      <div className="text-white font-semibold">{getSalary(jobInsights)}</div>
                    </div>
                    <div className="glass-card p-4 rounded-xl">
                      <div className="flex items-center mb-2">
                        <Clock className="w-4 h-4 mr-2 text-yellow-400" />
                        <span className="text-sm text-gray-400">Competition</span>
                      </div>
                      <div className="text-white font-semibold">{getCompetition(jobInsights)}</div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="glass-card p-12 rounded-3xl text-center">
                  <Search className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2">No Job Insights Yet</h3>
                  <p className="text-gray-400 mb-6">
                    Fill in the company and role information, then click "Get Job Insights" to see detailed information about your target position.
                  </p>
                </div>
              )}
            </motion.div>
          </div>

          {/* Generate Interview Button */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="mt-12 text-center"
          >
            <button
              onClick={generateInterview}
              className="btn-primary text-lg px-12 py-4"
            >
              Generate Interview
              <ArrowRight className="w-6 h-6 ml-3" />
            </button>
            <p className="text-gray-400 mt-4">
              AI will create personalized questions based on your resume and job insights
            </p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}

export default InterviewSetup
