import React, { useState, useCallback, useMemo } from 'react'
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

  const normalizeText = (value) => {
    if (value === null || value === undefined) return ''
    return String(value)
      .replace(/https?:\/\/\S+|www\.\S+/gi, '')
      .replace(/\bgithub\s*:\s*\S+/gi, '')
      .replace(/\bgithub\.com\/\S+/gi, '')
      .replace(/[•▸▪|]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .replace(/^[\s\-;,.]+|[\s\-;,.]+$/g, '')
  }

  const removeDuplicateSentences = (value) => {
    const text = normalizeText(value)
    const seen = new Set()
    return text
      .split(/(?<=[.!?])\s+|\s+-\s+/)
      .map(normalizeText)
      .filter((sentence) => {
        const key = sentence.toLowerCase().replace(/[^a-z0-9]+/g, '')
        if (!key || seen.has(key)) return false
        seen.add(key)
        return true
      })
      .join(' ')
  }

  const dedupeTextList = (values = []) => {
    const seen = new Set()
    return values
      .map((value) => removeDuplicateSentences(value))
      .filter((value) => {
        const key = value.toLowerCase().replace(/[^a-z0-9]+/g, '')
        if (!key || seen.has(key)) return false
        seen.add(key)
        return true
      })
  }

  const normalizeSkills = (skills) => {
    if (Array.isArray(skills)) return dedupeTextList(skills)
    if (skills && typeof skills === 'object') {
      return dedupeTextList(Object.values(skills).flat().filter(Boolean))
    }
    return []
  }

  const formatItem = (item, fields = []) => {
    if (typeof item === 'string') return normalizeText(item)
    if (!item || typeof item !== 'object') return ''
    return fields.map((field) => normalizeText(item[field])).filter(Boolean).join(' - ')
  }

  const cleanProjectDescription = (value, title = '') => {
    let text = normalizeText(value)
    if (title) {
      text = text.replace(new RegExp(title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i'), '')
    }
    text = text
      .replace(/\btech\s*stack\s*[:\-]\s*[^.]+/gi, ' ')
      .replace(/\btechnologies\s*(used)?\s*[:\-]\s*[^.]+/gi, ' ')
      .replace(/\btools\s*[:\-]\s*[^.]+/gi, ' ')
      .replace(/\bgithub\s*[:\-]?/gi, ' ')
      .replace(/\blink\s*[:\-]?/gi, ' ')
    text = removeDuplicateSentences(text)
    const words = text.split(/\s+/).filter(Boolean)
    return words.length > 45 ? `${words.slice(0, 45).join(' ')}.` : text
  }

  const cleanProjectTitle = (value) => normalizeText(value)
    .replace(/\b(project|github|tech stack|technologies|tools)\s*[:\-]\s*/gi, '')
    .replace(/^(JavaScript|HTML|CSS|React|Python|C\+\+|Java|Firebase|FastAPI|MongoDB|SQL|Node\.?js)\s+/i, '')
    .replace(/\b(built|developed|implemented|created)\b.*$/i, '')
    .slice(0, 90)
    .trim()

  const textSimilarity = (left, right) => {
    const stop = new Set(['the', 'and', 'with', 'that', 'this', 'from', 'for', 'used', 'using', 'html', 'css', 'javascript', 'react', 'python', 'java', 'project'])
    const leftTokens = new Set(normalizeText(left).toLowerCase().match(/[a-z0-9]+/g)?.filter((token) => token.length > 2 && !stop.has(token)) || [])
    const rightTokens = new Set(normalizeText(right).toLowerCase().match(/[a-z0-9]+/g)?.filter((token) => token.length > 2 && !stop.has(token)) || [])
    if (!leftTokens.size || !rightTokens.size) return 0
    let overlap = 0
    leftTokens.forEach((token) => {
      if (rightTokens.has(token)) overlap += 1
    })
    return overlap / Math.min(leftTokens.size, rightTokens.size)
  }

  const projectQualityScore = (project) => {
    const title = normalizeText(project.title)
    const description = normalizeText(project.description)
    let score = 0
    if (title.split(/\s+/).length >= 2 && title.split(/\s+/).length <= 8) score += 7
    if (title.split(/\s+/).length > 9) score -= 6
    if (/\b(built|developed|implemented|created|operations|demonstrated)\b/i.test(title)) score -= 5
    if (/\b(JavaScript|HTML|CSS|React|Python|C\+\+|Firebase|FastAPI|MongoDB)\b/i.test(title)) score -= 2
    if (description.split(/\s+/).length >= 8 && description.split(/\s+/).length <= 55) score += 5
    if (/\b(github|http|tech stack|technologies)\b/i.test(`${title} ${description}`)) score -= 8
    return score
  }

  const dedupeEducation = (education = []) => {
    const seen = new Set()
    return education
      .map((edu) => {
        if (typeof edu === 'string') {
          return { degree: normalizeText(edu), institution: '', year: '', score: '' }
        }
        return {
          degree: normalizeText(edu?.degree),
          institution: normalizeText(edu?.institution),
          year: normalizeText(edu?.year),
          score: normalizeText(edu?.score)
        }
      })
      .filter((edu) => {
        const degreeKey = edu.degree.toLowerCase().replace(/[^a-z0-9]+/g, '')
        const yearKey = edu.year.replace(/[^0-9]+/g, '')
        const scoreKey = edu.score.replace(/[^0-9.]+/g, '')
        const institutionKey = edu.institution.toLowerCase().replace(/[^a-z0-9]+/g, '').slice(0, 18)
        const key = `${degreeKey}|${yearKey}|${scoreKey || institutionKey}`
        if (!key.replace(/\|/g, '') || seen.has(key)) return false
        seen.add(key)
        return true
      })
  }

  const dedupeProjects = (projects = []) => {
    const unique = new Map()
    projects.forEach((project) => {
      const rawTitle = typeof project === 'string' ? '' : project?.title || project?.name || ''
      const rawDescription = typeof project === 'string'
        ? project
        : project?.description || project?.summary || project?.impact || ''
      let title = cleanProjectTitle(rawTitle)
      let description = cleanProjectDescription(rawDescription, title)
      if (!title && description) {
        title = cleanProjectTitle(description.split(/[:.]/)[0])
        description = cleanProjectDescription(description, title)
      }
      if (!title && !description) return

      const record = { title: title || 'Project', description }
      const recordText = `${record.title} ${record.description}`
      const recordScore = projectQualityScore(record)
      let replaced = false

      Array.from(unique.entries()).some(([key, existing]) => {
        const existingText = `${existing.title} ${existing.description}`
        const sameTitle = textSimilarity(record.title, existing.title) >= 0.75
        const sameContent = textSimilarity(recordText, existingText) >= 0.45
        if (sameTitle || sameContent) {
          if (recordScore > projectQualityScore(existing)) {
            unique.set(key, record)
          }
          replaced = true
          return true
        }
        return false
      })

      if (!replaced) {
        const key = recordText.toLowerCase().replace(/[^a-z0-9]+/g, '').slice(0, 220)
        unique.set(key, record)
      }
    })
    return Array.from(unique.values()).sort((left, right) => projectQualityScore(right) - projectQualityScore(left))
  }

  const cleanedExtractedData = useMemo(() => {
    if (!extractedData) return null
    return {
      ...extractedData,
      education: dedupeEducation(extractedData.education || []),
      projects: dedupeProjects(extractedData.projects || []),
      certifications: dedupeTextList(extractedData.certifications || []),
      achievements: dedupeTextList(extractedData.achievements || [])
    }
  }, [extractedData])

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
                    {normalizeSkills(cleanedExtractedData.skills).map((skill, index) => (
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
                    {(cleanedExtractedData.experience || []).map((exp, index) => (
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
                    {(cleanedExtractedData.education || []).map((edu, index) => (
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
                    {(cleanedExtractedData.projects || []).map((project, index) => (
                      <li key={`${project.title}-${index}`} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                        <h4 className="font-semibold text-white">{project.title}</h4>
                        {project.description && (
                          <p className="mt-2 text-sm leading-6 text-gray-300">{project.description}</p>
                        )}
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
