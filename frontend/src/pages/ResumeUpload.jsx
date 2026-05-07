import React, { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import { Upload, FileText, CheckCircle, AlertCircle, Sparkles, ArrowRight, X, Tag, Briefcase, GraduationCap } from 'lucide-react'
import apiService from '../api/api'

const ResumeUpload = () => {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [extractedData, setExtractedData] = useState(null)
  const [score, setScore] = useState(0)
  const navigate = useNavigate()

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = e.dataTransfer.files
    if (files && files[0]) {
      handleFileUpload(files[0])
    }
  }, [])

  const handleFileSelect = (e) => {
    const files = e.target.files
    if (files && files[0]) {
      handleFileUpload(files[0])
    }
  }

  const normalizeSkills = (skills) => {
    if (Array.isArray(skills)) return skills
    if (skills && typeof skills === 'object') {
      return Object.values(skills).flat().filter(Boolean)
    }
    return []
  }

  const formatItem = (item, fields = []) => {
    if (typeof item === 'string') return item
    if (!item || typeof item !== 'object') return ''
    return fields.map((field) => item[field]).filter(Boolean).join(' - ')
  }

  const handleFileUpload = async (uploadedFile) => {
    if (uploadedFile.type !== 'application/pdf') {
      alert('Please upload a PDF file')
      return
    }
    
    setFile(uploadedFile)
    setIsProcessing(true)

    try {
      const response = await apiService.uploadResume(uploadedFile)
      const analysis = response.analysis || {}
      const resumeScore = response.score || 0

      setExtractedData(analysis)
      setScore(resumeScore)
      sessionStorage.setItem('resumeAnalysis', JSON.stringify(analysis))
      sessionStorage.setItem('resumeScore', JSON.stringify(resumeScore))
    } catch (error) {
      console.error('Resume upload failed:', error)
      alert('Resume analysis failed. Please make sure the backend is running and try again.')
      setFile(null)
      setExtractedData(null)
      setScore(0)
    } finally {
      setIsProcessing(false)
    }
  }

  const removeFile = () => {
    setFile(null)
    setExtractedData(null)
    setScore(0)
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreMessage = (score) => {
    if (score >= 80) return 'Excellent Resume!'
    if (score >= 60) return 'Good Resume'
    return 'Needs Improvement'
  }

  return (
    <div className="min-h-screen relative">
      {/* Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-dark-bg via-dark-surface to-dark-bg">
        <div className="absolute inset-0 opacity-20">
          {[...Array(15)].map((_, i) => (
            <div
              key={i}
              className="absolute rounded-full bg-neon-blue opacity-10 animate-pulse-slow"
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
            <FileText className="w-8 h-8 text-neon-blue" />
            <span className="text-2xl font-bold text-gradient">Resume Analysis</span>
          </div>
          <Link to="/" className="text-gray-300 hover:text-white transition-colors">← Back</Link>
        </div>
      </nav>

      {/* Main Content */}
      <div className="relative z-10 container mx-auto px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto"
        >
          {!extractedData ? (
            <div className="text-center">
              <h1 className="text-4xl md:text-5xl font-bold text-gradient mb-6">
                Upload Your Resume
              </h1>
              <p className="text-xl text-gray-300 mb-12">
                AI will analyze your resume and extract key information for personalized interview preparation
              </p>

              {/* Upload Area */}
              <motion.div
                className={`relative glass-card p-12 rounded-3xl border-2 border-dashed transition-all duration-300 cursor-pointer ${
                  isDragging ? 'border-neon-blue bg-neon-blue/10' : 'border-glass-border hover:border-neon-blue/50'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  disabled={isProcessing}
                />
                
                <div className="text-center">
                  <motion.div
                    animate={isProcessing ? { rotate: 360 } : {}}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-neon-blue to-neon-purple mb-6"
                  >
                    {isProcessing ? (
                      <Sparkles className="w-10 h-10 text-white" />
                    ) : (
                      <Upload className="w-10 h-10 text-white" />
                    )}
                  </motion.div>
                  
                  <h3 className="text-2xl font-semibold mb-4">
                    {isProcessing ? 'Analyzing Resume...' : 'Drop your PDF here or click to browse'}
                  </h3>
                  
                  <p className="text-gray-400 mb-4">
                    PDF files up to 10MB
                  </p>
                  
                  {isProcessing && (
                    <div className="w-full max-w-md mx-auto">
                      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-neon-blue to-neon-purple"
                          initial={{ width: 0 }}
                          animate={{ width: '100%' }}
                          transition={{ duration: 3 }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>

              {/* File Preview */}
              <AnimatePresence>
                {file && !isProcessing && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="mt-6 glass-card p-6 rounded-2xl flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-4">
                      <FileText className="w-8 h-8 text-neon-blue" />
                      <div className="text-left">
                        <p className="font-semibold">{file.name}</p>
                        <p className="text-gray-400 text-sm">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>
                    </div>
                    <button
                      onClick={removeFile}
                      className="p-2 rounded-full hover:bg-red-500/20 transition-colors"
                    >
                      <X className="w-5 h-5 text-red-400" />
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ) : (
            /* Results Section */
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="text-center mb-12">
                <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
                <h1 className="text-4xl md:text-5xl font-bold text-gradient mb-6">
                  Resume Analysis Complete
                </h1>
                <p className="text-xl text-gray-300">
                  Your resume has been successfully analyzed
                </p>
              </div>

              {/* Score Card */}
              <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="glass-card p-8 rounded-3xl mb-8 text-center"
              >
                <div className={`text-6xl font-bold ${getScoreColor(score)} mb-4`}>
                  {score}/100
                </div>
                <div className={`text-xl ${getScoreColor(score)} mb-2`}>
                  {getScoreMessage(score)}
                </div>
                <div className="text-gray-400">
                  Resume strength score based on skills, experience, and formatting
                </div>
              </motion.div>

              {/* Extracted Data Grid */}
              <div className="grid md:grid-cols-2 gap-6 mb-8">
                {/* Skills */}
                <motion.div
                  initial={{ x: -50, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.3 }}
                  className="glass-card p-6 rounded-2xl"
                >
                  <div className="flex items-center space-x-2 mb-4">
                    <Tag className="w-5 h-5 text-neon-cyan" />
                    <h3 className="text-xl font-semibold">Skills Extracted</h3>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {normalizeSkills(extractedData.skills).map((skill, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 rounded-full bg-neon-blue/20 text-neon-cyan text-sm border border-neon-blue/30"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </motion.div>

                {/* Experience */}
                <motion.div
                  initial={{ x: 50, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.4 }}
                  className="glass-card p-6 rounded-2xl"
                >
                  <div className="flex items-center space-x-2 mb-4">
                    <Briefcase className="w-5 h-5 text-neon-cyan" />
                    <h3 className="text-xl font-semibold">Experience</h3>
                  </div>
                  <ul className="space-y-2">
                    {(extractedData.experience || []).map((exp, index) => (
                      <li key={index} className="text-gray-300 text-sm">
                        • {formatItem(exp, ['role', 'company', 'duration'])}
                      </li>
                    ))}
                  </ul>
                </motion.div>

                {/* Education */}
                <motion.div
                  initial={{ x: -50, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.5 }}
                  className="glass-card p-6 rounded-2xl"
                >
                  <div className="flex items-center space-x-2 mb-4">
                    <GraduationCap className="w-5 h-5 text-neon-cyan" />
                    <h3 className="text-xl font-semibold">Education</h3>
                  </div>
                  <ul className="space-y-2">
                    {(extractedData.education || []).map((edu, index) => (
                      <li key={index} className="text-gray-300 text-sm">
                        • {formatItem(edu, ['degree', 'institution', 'year', 'score'])}
                      </li>
                    ))}
                  </ul>
                </motion.div>

                {/* Projects */}
                <motion.div
                  initial={{ x: 50, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.6 }}
                  className="glass-card p-6 rounded-2xl"
                >
                  <div className="flex items-center space-x-2 mb-4">
                    <Sparkles className="w-5 h-5 text-neon-cyan" />
                    <h3 className="text-xl font-semibold">Projects</h3>
                  </div>
                  <ul className="space-y-2">
                    {(extractedData.projects || []).map((project, index) => (
                      <li key={index} className="text-gray-300 text-sm">
                        • {formatItem(project, ['title', 'description', 'impact'])}
                      </li>
                    ))}
                  </ul>
                </motion.div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={removeFile}
                  className="btn-secondary"
                >
                  Upload Different Resume
                </button>
                <Link to="/setup" className="btn-primary">
                  Continue to Interview Setup
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default ResumeUpload
