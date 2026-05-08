import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Link, useLocation } from 'react-router-dom'
import { CheckCircle, AlertCircle, TrendingUp, MessageSquare, Star, ArrowRight, Brain, Lightbulb, Target, Zap, Download, Share2, Mail, RefreshCw } from 'lucide-react'
import apiService from '../api/api'

const readStoredJson = (key, fallback = null) => {
  try {
    return JSON.parse(localStorage.getItem(key) || sessionStorage.getItem(key) || 'null') || fallback
  } catch {
    return fallback
  }
}

const attachCandidateToReport = (report, profile) => {
  const linkedReport = {
    ...report,
    userId: profile?.userId || report.userId || '',
    candidateName: profile?.fullName || report.candidateName || '',
    candidateEmail: profile?.email || report.candidateEmail || '',
    sessionId: profile?.sessionId || report.sessionId || report.session_id || '',
    interviewId: report.interviewId || report.session_id || ''
  }

  console.log('Report linked to candidateEmail', linkedReport.candidateEmail)
  return linkedReport
}

const FeedbackPanel = () => {
  const location = useLocation()
  const storedReport = JSON.parse(sessionStorage.getItem('interviewReport') || '{}')
  const report = location.state?.report || storedReport
  const hasReport = Boolean(report && Object.keys(report).length)
  const [feedbackData, setFeedbackData] = useState(() => {
    if (!hasReport) return null

    const categoryScores = report.category_scores || {}
    return {
      overallScore: Math.round(report.overall_score || 0),
      strengths: report.strengths?.length ? report.strengths : ['Interview completed successfully'],
      improvements: report.improvements?.length ? report.improvements : report.recommendations || [],
      followUpQuestion: report.next_steps?.[0] || 'Practice one answer again using a clear situation, action, and result.',
      detailedFeedback: {
        technical: Math.round(categoryScores.technical || 0),
        communication: Math.round(categoryScores.communication || 0),
        confidence: Math.round(categoryScores.confidence || 0),
        behavior: Math.round(categoryScores.behavior || categoryScores.behavioral || 0),
        completeness: Math.round(categoryScores.completeness || 0)
      },
      keyInsights: report.recommendations?.length ? report.recommendations : ['Review your evaluated answers and repeat the interview for a better baseline.'],
      replayTimeline: report.replay_timeline || [],
      strongestAnswer: report.strongest_answer,
      weakestAnswer: report.weakest_answer
    }
  })
  const [isGenerating, setIsGenerating] = useState(!hasReport)
  const [emailAutomation, setEmailAutomation] = useState(null)
  const [isEmailing, setIsEmailing] = useState(false)

  useEffect(() => {
    if (hasReport) return
    setIsGenerating(false)
    setFeedbackData({
      overallScore: 0,
      strengths: [],
      improvements: ['Complete a voice interview to generate a real report.'],
      followUpQuestion: 'Start a new interview to receive a practice question.',
      detailedFeedback: { technical: 0, communication: 0, confidence: 0, behavior: 0, completeness: 0 },
      keyInsights: ['No evaluated answers are available yet.'],
      replayTimeline: []
    })
  }, [])

  useEffect(() => {
    if (!hasReport) return

    const profile = readStoredJson('candidateProfile')
    if (!profile?.email) {
      setEmailAutomation({ emailStatus: 'missing_profile' })
      return
    }

    const automationKey = `reportEmailAutomation:${report.session_id || report.generated_at || 'latest'}`
    const storedAutomation = readStoredJson(automationKey)
    if (storedAutomation) {
      setEmailAutomation(storedAutomation)
      return
    }

    let isMounted = true
    const runAutomation = async () => {
      setIsEmailing(true)
      try {
        const linkedReport = attachCandidateToReport(report, profile)
        const result = await apiService.completeReportAutomation(linkedReport, profile, linkedReport.interviewId || linkedReport.sessionId || '')
        sessionStorage.setItem(automationKey, JSON.stringify(result))
        if (isMounted) setEmailAutomation(result)
      } catch (error) {
        const failed = {
          emailStatus: 'failed',
          emailError: error?.response?.data?.detail || 'Report email automation failed.'
        }
        sessionStorage.setItem(automationKey, JSON.stringify(failed))
        if (isMounted) setEmailAutomation(failed)
      } finally {
        if (isMounted) setIsEmailing(false)
      }
    }

    runAutomation()
    return () => {
      isMounted = false
    }
  }, [hasReport, report.session_id, report.generated_at])

  const resendReportEmail = async () => {
    const profile = readStoredJson('candidateProfile')
    if (!profile?.email) {
      setEmailAutomation({ emailStatus: 'missing_profile' })
      return
    }

    setIsEmailing(true)
    try {
      const linkedReport = attachCandidateToReport(report, profile)
      const result = await apiService.completeReportAutomation(linkedReport, profile, linkedReport.interviewId || linkedReport.sessionId || '')
      setEmailAutomation(result)
      sessionStorage.setItem(`reportEmailAutomation:${report.session_id || report.generated_at || 'latest'}`, JSON.stringify(result))
    } catch (error) {
      setEmailAutomation({
        emailStatus: 'failed',
        emailError: error?.response?.data?.detail || 'Report email automation failed.'
      })
    } finally {
      setIsEmailing(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'from-green-500/20 to-green-400/20'
    if (score >= 60) return 'from-yellow-500/20 to-yellow-400/20'
    return 'from-red-500/20 to-red-400/20'
  }

  const pdfDownloadUrl = emailAutomation?.pdf?.pdfUrl
    ? `${apiService.baseURL}${emailAutomation.pdf.pdfUrl}`
    : ''

  const emailStatusContent = () => {
    if (isEmailing) {
      return {
        tone: 'border-neon-blue/30 bg-neon-blue/10 text-neon-cyan',
        title: 'Preparing PDF report',
        detail: 'Generating your PDF and sending it to the candidate email.'
      }
    }
    if (emailAutomation?.emailStatus === 'sent_via_brevo') {
      return {
        tone: 'border-green-400/30 bg-green-500/10 text-green-200',
        title: 'Report emailed successfully',
        detail: 'The PDF report was delivered using Brevo.'
      }
    }
    if (emailAutomation?.emailStatus === 'sent_via_resend') {
      return {
        tone: 'border-yellow-400/30 bg-yellow-500/10 text-yellow-200',
        title: 'Brevo failed - sent using backup provider',
        detail: 'The PDF report was delivered using Resend fallback.'
      }
    }
    if (emailAutomation?.emailStatus === 'missing_profile') {
      return {
        tone: 'border-yellow-400/30 bg-yellow-500/10 text-yellow-200',
        title: 'Candidate profile is required',
        detail: 'Add your name and email to enable automatic PDF report delivery.'
      }
    }
    if (emailAutomation?.emailStatus === 'failed') {
      return {
        tone: 'border-red-400/30 bg-red-500/10 text-red-200',
        title: 'Email delivery failed',
        detail: emailAutomation.emailError || 'The PDF was generated, but email delivery could not be completed.'
      }
    }
    return {
      tone: 'border-white/10 bg-white/[0.04] text-gray-300',
      title: 'Report email automation',
      detail: 'Your PDF report will be emailed after the final report is ready.'
    }
  }

  if (isGenerating) {
    return (
      <div className="min-h-screen relative flex items-center justify-center">
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

        <div className="relative z-10 text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-neon-blue to-neon-purple mb-6"
          >
            <Brain className="w-10 h-10 text-white" />
          </motion.div>
          <h2 className="text-2xl font-bold text-gradient mb-4">AI is Analyzing Your Performance</h2>
          <p className="text-gray-400 mb-8">Generating personalized feedback and insights...</p>
          
          <div className="w-64 h-2 bg-gray-700 rounded-full overflow-hidden mx-auto">
            <motion.div
              className="h-full bg-gradient-to-r from-neon-blue to-neon-purple"
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 3 }}
            />
          </div>
        </div>
      </div>
    )
  }

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
            <MessageSquare className="w-8 h-8 text-neon-blue" />
            <span className="text-2xl font-bold text-gradient">Interview Feedback</span>
          </div>
          <Link to="/interview" className="text-gray-300 hover:text-white transition-colors">← Back</Link>
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
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-gradient mb-6">
              Your Interview Analysis
            </h1>
            <p className="text-xl text-gray-300">
              AI-powered insights to help you ace your next interview
            </p>
          </div>

          {/* Overall Score */}
          <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-center mb-12"
          >
            <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-r ${getScoreBgColor(feedbackData.overallScore)} border-2 border-neon-blue/30`}>
              <div>
                <div className={`text-4xl font-bold ${getScoreColor(feedbackData.overallScore)}`}>
                  {feedbackData.overallScore}
                </div>
                <div className="text-sm text-gray-400">Overall Score</div>
              </div>
            </div>
          </motion.div>

          {/* PDF + Email Status */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.25 }}
            className={`mb-12 rounded-3xl border p-5 ${emailStatusContent().tone}`}
          >
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div className="flex items-start gap-3">
                <div className="mt-1 rounded-2xl bg-white/10 p-2">
                  <Mail className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{emailStatusContent().title}</h3>
                  <p className="mt-1 text-sm opacity-90">{emailStatusContent().detail}</p>
                </div>
              </div>
              <div className="flex flex-col gap-3 sm:flex-row">
                {pdfDownloadUrl && (
                  <a href={pdfDownloadUrl} target="_blank" rel="noreferrer" className="btn-secondary justify-center">
                    <Download className="mr-2 h-4 w-4" />
                    Download PDF
                  </a>
                )}
                <button
                  onClick={resendReportEmail}
                  disabled={isEmailing}
                  className="btn-secondary justify-center disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <RefreshCw className={`mr-2 h-4 w-4 ${isEmailing ? 'animate-spin' : ''}`} />
                  Resend Email
                </button>
              </div>
            </div>
          </motion.div>

          {/* Detailed Scores Grid */}
          <div className="grid md:grid-cols-5 gap-4 mb-12">
            {Object.entries(feedbackData.detailedFeedback).map(([key, value], index) => (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                className="glass-card p-6 rounded-2xl text-center"
              >
                <div className={`text-2xl font-bold ${getScoreColor(value)} mb-2`}>
                  {value}
                </div>
                <div className="text-sm text-gray-400 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </div>
                <div className="mt-3 w-full bg-gray-700 rounded-full h-2">
                  <motion.div
                    className={`h-2 rounded-full bg-gradient-to-r ${
                      value >= 80 ? 'from-green-500 to-green-400' :
                      value >= 60 ? 'from-yellow-500 to-yellow-400' :
                      'from-red-500 to-red-400'
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${value}%` }}
                    transition={{ duration: 0.8, delay: 0.5 + index * 0.1 }}
                  />
                </div>
              </motion.div>
            ))}
          </div>

          <div className="grid lg:grid-cols-2 gap-8 mb-12">
            {/* Strengths */}
            <motion.div
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="glass-card p-8 rounded-3xl"
            >
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                </div>
                <h3 className="text-2xl font-semibold">Your Strengths</h3>
              </div>
              <ul className="space-y-4">
                {feedbackData.strengths.map((strength, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                    className="flex items-start space-x-3"
                  >
                    <Star className="w-5 h-5 text-yellow-400 mt-1 flex-shrink-0" />
                    <span className="text-gray-300">{strength}</span>
                  </motion.li>
                ))}
              </ul>
            </motion.div>

            {/* Areas for Improvement */}
            <motion.div
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="glass-card p-8 rounded-3xl"
            >
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 rounded-full bg-yellow-500/20 flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-yellow-400" />
                </div>
                <h3 className="text-2xl font-semibold">Areas to Improve</h3>
              </div>
              <ul className="space-y-4">
                {feedbackData.improvements.map((improvement, index) => (
                  <motion.li
                    key={index}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
                    className="flex items-start space-x-3"
                  >
                    <Lightbulb className="w-5 h-5 text-neon-cyan mt-1 flex-shrink-0" />
                    <span className="text-gray-300">{improvement}</span>
                  </motion.li>
                ))}
              </ul>
            </motion.div>
          </div>

          {/* Follow-up Question */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.7 }}
            className="glass-card p-8 rounded-3xl mb-12 bg-gradient-to-r from-neon-blue/10 to-neon-purple/10"
          >
            <div className="flex items-center space-x-3 mb-4">
              <Target className="w-6 h-6 text-neon-cyan" />
              <h3 className="text-2xl font-semibold">Practice Question</h3>
            </div>
            <p className="text-lg text-gray-300 mb-6">
              {feedbackData.followUpQuestion}
            </p>
            <button className="btn-secondary">
              Practice This Question
              <ArrowRight className="w-5 h-5 ml-2" />
            </button>
          </motion.div>

          {/* Key Insights */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="glass-card p-8 rounded-3xl mb-12"
          >
            <div className="flex items-center space-x-3 mb-6">
              <TrendingUp className="w-6 h-6 text-neon-cyan" />
              <h3 className="text-2xl font-semibold">Key Insights</h3>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              {feedbackData.keyInsights.map((insight, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: 0.9 + index * 0.1 }}
                  className="p-4 rounded-xl bg-glass-border"
                >
                  <Zap className="w-5 h-5 text-yellow-400 mb-2" />
                  <p className="text-gray-300">{insight}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Replay Timeline */}
          {feedbackData.replayTimeline?.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.9 }}
              className="glass-card p-8 rounded-3xl mb-12"
            >
              <div className="flex items-center space-x-3 mb-6">
                <MessageSquare className="w-6 h-6 text-neon-cyan" />
                <h3 className="text-2xl font-semibold">Replay Timeline</h3>
              </div>
              <div className="space-y-4">
                {feedbackData.replayTimeline.map((item, index) => {
                  const questionText = typeof item.question === 'string' ? item.question : item.question?.question
                  const explanation = item.feedback?.deep_explanation
                  return (
                    <div key={index} className="p-5 rounded-xl bg-glass-border">
                      <div className="flex justify-between gap-4 mb-3">
                        <p className="font-semibold text-white">{questionText}</p>
                        <span className="text-neon-cyan font-bold">{Math.round(item.score || 0)}</span>
                      </div>
                      <p className="text-sm text-gray-300 mb-3">{item.answer}</p>
                      <p className="text-sm text-yellow-200 mb-2">{item.feedback?.detailed_feedback}</p>
                      {explanation && (
                        <div className="mt-3 grid md:grid-cols-2 gap-3 text-sm">
                          <div>
                            <div className="text-gray-400 mb-1">Missing</div>
                            <ul className="text-gray-300 list-disc list-inside">
                              {(explanation.what_was_missing || []).map((point, idx) => <li key={idx}>{point}</li>)}
                            </ul>
                          </div>
                          <div>
                            <div className="text-gray-400 mb-1">Improved Structure</div>
                            <p className="text-gray-300">{explanation.improved_answer}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </motion.div>
          )}

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.0 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Link to="/dashboard" className="btn-primary text-lg">
              View Full Dashboard
              <TrendingUp className="w-5 h-5 ml-2" />
            </Link>
            {pdfDownloadUrl ? (
              <a href={pdfDownloadUrl} target="_blank" rel="noreferrer" className="btn-secondary text-lg flex items-center justify-center">
                <Download className="w-5 h-5 mr-2" />
                Download Report
              </a>
            ) : (
            <button className="btn-secondary text-lg flex items-center justify-center" disabled>
              <Download className="w-5 h-5 mr-2" />
              Download Report
            </button>
            )}
            <button className="btn-secondary text-lg flex items-center justify-center">
              <Share2 className="w-5 h-5 mr-2" />
              Share Results
            </button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}

export default FeedbackPanel
