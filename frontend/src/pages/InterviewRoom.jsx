import React, { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Camera, Mic, MicOff, Video, VideoOff, Brain, Volume2, Eye, Activity, Clock, MessageSquare, StopCircle, PlayCircle, Send, Keyboard } from 'lucide-react'
import { FaceMesh } from '@mediapipe/face_mesh'
import apiService from '../api/api'

const InterviewRoom = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const storedInterviewState = JSON.parse(sessionStorage.getItem('interviewState') || '{}')
  const interviewState = location.state || storedInterviewState
  const [isInterviewActive, setIsInterviewActive] = useState(false)
  const [isMicOn, setIsMicOn] = useState(true)
  const [isCameraOn, setIsCameraOn] = useState(true)
  const [currentQuestion, setCurrentQuestion] = useState('')
  const [isAISpeaking, setIsAISpeaking] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [timer, setTimer] = useState(0)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [eyeContact, setEyeContact] = useState(85)
  const [attention, setAttention] = useState(92)
  const [faceDetected, setFaceDetected] = useState(true)
  const [behaviorState, setBehaviorState] = useState('Camera Off')
  const [distractionCount, setDistractionCount] = useState(0)
  const [transcript, setTranscript] = useState('')
  const [audioLevel, setAudioLevel] = useState(0)
  const [answers, setAnswers] = useState([])
  const [chatMessages, setChatMessages] = useState([])
  const [answerMode, setAnswerMode] = useState('voice')
  const [typedAnswer, setTypedAnswer] = useState('')
  const [isEvaluating, setIsEvaluating] = useState(false)
  
  const videoRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const recognitionRef = useRef(null)
  const timerIntervalRef = useRef(null)
  const faceMeshRef = useRef(null)
  const behaviorIntervalRef = useRef(null)
  const chatEndRef = useRef(null)
  const answerModeRef = useRef(answerMode)

  const initialInterviewQuestions = interviewState.questions?.length ? interviewState.questions : [
    "Tell me about yourself and your experience relevant to this role.",
    "What interests you most about this position and our company?",
    "Describe a challenging project you've worked on and how you overcame obstacles.",
    "How do you stay updated with the latest technologies and industry trends?",
    "Where do you see yourself professionally in the next 3-5 years?"
  ]
  const [activeQuestions, setActiveQuestions] = useState(initialInterviewQuestions)

  const getQuestionText = (question) => {
    if (!question) return ''
    return typeof question === 'string' ? question : question.question
  }

  const getQuestionRound = (question) => {
    if (!question || typeof question === 'string') return 'General'
    return question.round || 'General'
  }

  useEffect(() => {
    if (isInterviewActive) {
      startTimer()
    } else {
      stopTimer()
    }
    
    return () => stopTimer()
  }, [isInterviewActive])

  useEffect(() => {
    if (isInterviewActive) {
      askQuestion(currentQuestionIndex)
    }
  }, [isInterviewActive, currentQuestionIndex])

  useEffect(() => {
    if (isInterviewActive && isCameraOn) {
      startBehaviorTracking()
    } else {
      stopBehaviorTracking()
      if (!isCameraOn) setBehaviorState('Camera Off')
    }

    return () => stopBehaviorTracking()
  }, [isInterviewActive, isCameraOn])

  useEffect(() => {
    // Simulate audio level changes
    const audioInterval = setInterval(() => {
      if (isListening) {
        setAudioLevel(Math.random() * 100)
      } else {
        setAudioLevel(0)
      }
    }, 100)

    return () => clearInterval(audioInterval)
  }, [isListening])

  useEffect(() => {
    answerModeRef.current = answerMode

    if (answerMode === 'text') {
      stopSpeechRecognition()
      return
    }

    if (isInterviewActive && !isAISpeaking && isMicOn) {
      setIsListening(true)
      startSpeechRecognition()
    }
  }, [answerMode, isInterviewActive, isAISpeaking, isMicOn])

  const startTimer = () => {
    stopTimer()
    timerIntervalRef.current = setInterval(() => {
      setTimer(prev => prev + 1)
    }, 1000)
  }

  const stopTimer = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current)
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const appendChatMessage = useCallback((message) => {
    setChatMessages(prev => {
      const id = message.id || `${message.role}-${Date.now()}`
      if (prev.some(item => item.id === id)) return prev
      return [
        ...prev,
        {
          ...message,
          id,
          timestamp: message.timestamp || formatTime(timer)
        }
      ]
    })
  }, [timer])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [chatMessages, transcript])

  const askQuestion = (index) => {
    if (index < activeQuestions.length) {
      const nextQuestionData = activeQuestions[index]
      setCurrentQuestion(nextQuestionData)
      setIsAISpeaking(true)
      appendChatMessage({
        id: `ai-question-${index}`,
        role: 'ai',
        label: getQuestionRound(nextQuestionData),
        text: getQuestionText(nextQuestionData)
      })
      speakQuestion(getQuestionText(nextQuestionData))
    } else {
      endInterview()
    }
  }

  const speakQuestion = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 0.9
      utterance.pitch = 1
      utterance.onend = () => {
        setIsAISpeaking(false)
        if (answerModeRef.current === 'voice' && isMicOn) {
          setIsListening(true)
          startSpeechRecognition()
        }
      }
      window.speechSynthesis.speak(utterance)
    } else {
      setIsAISpeaking(false)
      if (answerModeRef.current === 'voice' && isMicOn) {
        setIsListening(true)
      }
    }
  }

  const startSpeechRecognition = () => {
    if (recognitionRef.current) return

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = true
      recognitionRef.current.interimResults = true

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = ''
        let interimTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' '
          } else {
            interimTranscript += transcript
          }
        }

        setTranscript(finalTranscript + interimTranscript)
      }

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
      }

      recognitionRef.current.start()
    }
  }

  const stopSpeechRecognition = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      recognitionRef.current = null
    }
    setIsListening(false)
  }

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 },
        audio: false 
      })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
      setIsCameraOn(true)
      setBehaviorState('Attentive')
    } catch (error) {
      console.error('Error accessing camera:', error)
      setIsCameraOn(false)
      setBehaviorState('Camera Permission Denied')
    }
  }

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject
      const tracks = stream.getTracks()
      tracks.forEach(track => track.stop())
      videoRef.current.srcObject = null
    }
    setIsCameraOn(false)
    setFaceDetected(false)
    setBehaviorState('Camera Off')
  }

  const startBehaviorTracking = () => {
    if (!videoRef.current || behaviorIntervalRef.current) return

    if (!faceMeshRef.current) {
      faceMeshRef.current = new FaceMesh({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
      })
      faceMeshRef.current.setOptions({
        maxNumFaces: 1,
        refineLandmarks: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
      })
      faceMeshRef.current.onResults(handleFaceMeshResults)
    }

    behaviorIntervalRef.current = setInterval(async () => {
      if (videoRef.current?.readyState >= 2 && faceMeshRef.current) {
        try {
          await faceMeshRef.current.send({ image: videoRef.current })
        } catch (error) {
          console.error('Face tracking failed:', error)
        }
      }
    }, 700)
  }

  const stopBehaviorTracking = () => {
    if (behaviorIntervalRef.current) {
      clearInterval(behaviorIntervalRef.current)
      behaviorIntervalRef.current = null
    }
  }

  const handleFaceMeshResults = (results) => {
    const brightness = estimateBrightness(videoRef.current)
    if (brightness < 35) {
      setBehaviorState('Eyes Not Visible')
      setAttention(prev => Math.max(0, prev - 8))
      setEyeContact(prev => Math.max(0, prev - 10))
      setDistractionCount(prev => prev + 1)
      return
    }

    const landmarks = results.multiFaceLandmarks?.[0]
    if (!landmarks) {
      setFaceDetected(false)
      setBehaviorState('No Face Detected')
      setAttention(prev => Math.max(0, prev - 12))
      setEyeContact(prev => Math.max(0, prev - 12))
      setDistractionCount(prev => prev + 1)
      return
    }

    setFaceDetected(true)
    const nose = landmarks[1]
    const leftEye = landmarks[33]
    const rightEye = landmarks[263]
    const eyeCenterX = (leftEye.x + rightEye.x) / 2
    const gazeOffset = Math.abs(nose.x - eyeCenterX)
    const lookingAway = gazeOffset > 0.075
    const eyeScore = Math.max(0, Math.min(100, 100 - gazeOffset * 900))

    setEyeContact(Math.round(eyeScore))
    setAttention(Math.round(lookingAway ? Math.max(35, eyeScore - 20) : Math.min(100, eyeScore + 5)))
    setBehaviorState(lookingAway ? 'Looking Away' : 'Attentive')
    if (lookingAway) setDistractionCount(prev => prev + 1)
  }

  const estimateBrightness = (video) => {
    if (!video) return 0
    const canvas = document.createElement('canvas')
    canvas.width = 32
    canvas.height = 24
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data
    let total = 0
    for (let i = 0; i < data.length; i += 4) {
      total += (data[i] + data[i + 1] + data[i + 2]) / 3
    }
    return total / (data.length / 4)
  }

  const startInterview = () => {
    setActiveQuestions(initialInterviewQuestions)
    setIsInterviewActive(true)
    setCurrentQuestionIndex(0)
    setTimer(0)
    setChatMessages([])
    setTranscript('')
    setTypedAnswer('')
    startCamera()
  }

  const evaluateCurrentAnswer = async (answerOverride = null, modeOverride = answerMode) => {
    const answerText = (answerOverride ?? transcript).trim()
    if (!answerText || !currentQuestion) return null
    if (isEvaluating) return null

    setIsEvaluating(true)

    const behaviorData = {
      eye_contact: eyeContact,
      attention,
      face_detected: faceDetected,
      distraction_count: distractionCount,
      behavior_state: behaviorState,
      confidence_indicators: {
        clear_voice: modeOverride === 'voice' ? (audioLevel > 10 ? 0.8 : 0.5) : null,
        steady_pace: modeOverride === 'voice' ? 0.7 : null,
        minimal_fillers: modeOverride === 'voice' ? 0.6 : null,
        input_mode: modeOverride
      }
    }

    try {
      const response = await apiService.evaluateAnswer({
        question: currentQuestion,
        answer: answerText,
        question_type: typeof currentQuestion === 'string' ? 'general' : currentQuestion.type,
        behavior_data: behaviorData,
        resume_context: interviewState.resumeData || {},
        job_insights: interviewState.jobInsights || {}
      })

      const answerRecord = {
        question: currentQuestion,
        answer: answerText,
        scores: response.evaluation?.scores || {},
        feedback: response.evaluation?.feedback || {},
        behavior_data: behaviorData,
        input_mode: modeOverride
      }

      appendChatMessage({
        role: 'user',
        label: modeOverride === 'voice' ? 'Your voice answer' : 'Your typed answer',
        text: answerText
      })

      const feedbackSummary =
        response.evaluation?.feedback?.detailed_feedback ||
        response.evaluation?.feedback?.summary ||
        response.evaluation?.feedback?.overall_feedback

      if (feedbackSummary) {
        appendChatMessage({
          role: 'ai',
          label: `Evaluation ${response.evaluation?.scores?.overall ?? ''}`.trim(),
          text: feedbackSummary
        })
      }

      setAnswers(prev => [...prev, answerRecord])
      return answerRecord
    } catch (error) {
      console.error('Answer evaluation failed:', error)
      const fallbackRecord = {
        question: currentQuestion,
        answer: answerText,
        scores: { overall: 0 },
        feedback: {},
        behavior_data: behaviorData,
        input_mode: modeOverride
      }
      appendChatMessage({
        role: 'user',
        label: modeOverride === 'voice' ? 'Your voice answer' : 'Your typed answer',
        text: answerText
      })
      appendChatMessage({
        role: 'ai',
        label: 'Evaluation unavailable',
        text: 'I could not evaluate this answer because the evaluation service did not respond.'
      })
      setAnswers(prev => [...prev, fallbackRecord])
      return fallbackRecord
    } finally {
      setIsEvaluating(false)
    }
  }

  const endInterview = async (skipCurrentEvaluation = false, providedAnswers = null) => {
    setIsInterviewActive(false)
    setIsAISpeaking(false)
    setIsListening(false)
    stopSpeechRecognition()
    stopCamera()

    const latestAnswer = skipCurrentEvaluation
      ? null
      : await evaluateCurrentAnswer(answerMode === 'text' ? typedAnswer : null, answerMode)
    const finalAnswers = providedAnswers || (latestAnswer ? [...answers, latestAnswer] : answers)

    try {
      const response = await apiService.endInterviewSession({
        session_id: interviewState.sessionId || `session_${Date.now()}`,
        user_id: 'user_123',
        company: interviewState.company || 'Unknown',
        role: interviewState.role || 'Unknown',
        questions: activeQuestions,
        answers: finalAnswers,
        behavior_data: finalAnswers.map(item => item.behavior_data || {}),
        answer_modes: finalAnswers.map(item => item.input_mode || 'voice'),
        scores: {}
      })

      sessionStorage.setItem('interviewReport', JSON.stringify(response.report || {}))
      navigate('/feedback', { state: { report: response.report || {} } })
    } catch (error) {
      console.error('Final report failed:', error)
      navigate('/feedback')
    }
  }

  const maybeInsertFollowupQuestion = async (answerRecord, finalAnswers) => {
    if (!answerRecord || !currentQuestion || currentQuestion?.is_followup) return false

    try {
      const response = await apiService.generateFollowupQuestion({
        question: currentQuestion,
        answer: answerRecord.answer,
        question_type: typeof currentQuestion === 'string' ? 'general' : currentQuestion.type,
        behavior_data: {
          score: answerRecord.scores?.overall || 0,
          missing_points: answerRecord.feedback?.missing_points || []
        },
        resume_context: interviewState.resumeData || {},
        job_insights: interviewState.jobInsights || {},
        evaluation: {
          scores: answerRecord.scores || {},
          feedback: answerRecord.feedback || {},
          overall_score: answerRecord.scores?.overall || 0
        },
        previous_answers: finalAnswers.slice(-6)
      })

      if (!response?.required || !response.followup_question) return false

      setActiveQuestions(prev => {
        const followupId = response.followup_question.id
        if (prev.some(question => typeof question !== 'string' && question.id === followupId)) {
          return prev
        }
        const next = [...prev]
        next.splice(currentQuestionIndex + 1, 0, response.followup_question)
        return next
      })

      appendChatMessage({
        role: 'ai',
        label: 'Adaptive follow-up',
        text: response.followup_question.question
      })

      return true
    } catch (error) {
      console.error('Follow-up generation failed:', error)
      return false
    }
  }

  const nextQuestion = async () => {
    stopSpeechRecognition()
    const evaluated = await evaluateCurrentAnswer(null, 'voice')
    const finalAnswers = evaluated ? [...answers, evaluated] : answers
    const insertedFollowup = await maybeInsertFollowupQuestion(evaluated, finalAnswers)

    setTranscript('')

    if (insertedFollowup || currentQuestionIndex < activeQuestions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
    } else {
      await endInterview(true, finalAnswers)
    }
  }

  const submitTypedAnswer = async () => {
    const answerText = typedAnswer.trim()
    if (!answerText || isAISpeaking || isEvaluating || !isInterviewActive) return

    const evaluated = await evaluateCurrentAnswer(answerText, 'text')
    if (!evaluated) return

    setTypedAnswer('')
    setTranscript('')

    const finalAnswers = [...answers, evaluated]
    const insertedFollowup = await maybeInsertFollowupQuestion(evaluated, finalAnswers)

    if (insertedFollowup || currentQuestionIndex < activeQuestions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
    } else {
      await endInterview(true, finalAnswers)
    }
  }

  const handleTextKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      submitTypedAnswer()
    }
  }

  const toggleMic = () => {
    if (answerMode === 'text') return
    if (isMicOn) {
      stopSpeechRecognition()
    } else if (isInterviewActive && !isAISpeaking) {
      setIsListening(true)
      startSpeechRecognition()
    }
    setIsMicOn(!isMicOn)
  }

  const toggleCamera = () => {
    if (isCameraOn) {
      stopCamera()
    } else {
      startCamera()
    }
  }

  return (
    <div className="min-h-screen relative bg-dark-bg">
      {/* Background Effects */}
      <div className="fixed inset-0 bg-gradient-to-br from-dark-bg via-dark-surface to-dark-bg">
        <div className="absolute inset-0 opacity-10">
          {[...Array(10)].map((_, i) => (
            <div
              key={i}
              className="absolute rounded-full bg-neon-blue animate-pulse-slow"
              style={{
                width: Math.random() * 60 + 30 + 'px',
                height: Math.random() * 60 + 30 + 'px',
                left: Math.random() * 100 + '%',
                top: Math.random() * 100 + '%',
                animationDelay: Math.random() * 5 + 's',
                animationDuration: Math.random() * 6 + 6 + 's'
              }}
            />
          ))}
        </div>
      </div>

      {/* Header */}
      <div className="relative z-10 glass-card mx-4 mt-4 px-6 py-3 rounded-2xl">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <Brain className="w-6 h-6 text-neon-blue" />
            <span className="text-xl font-bold text-gradient">AI Interview Room</span>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-neon-cyan" />
              <span className="font-mono text-neon-cyan">{formatTime(timer)}</span>
            </div>
            <Link to="/setup" className="text-gray-300 hover:text-white transition-colors">Exit</Link>
          </div>
        </div>
      </div>

      {/* Main Interview Interface */}
      <div className="relative z-10 container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-12 gap-6 h-[calc(100vh-120px)]">
          
          {/* Left Side - AI Avatar */}
          <motion.div
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6 }}
            className="lg:col-span-3"
          >
            <div className="glass-card p-6 rounded-2xl h-full flex flex-col">
              <h3 className="text-lg font-semibold mb-4 text-center">AI Interviewer</h3>
              
              {/* AI Avatar */}
              <div className="flex-1 flex items-center justify-center">
                <motion.div
                  animate={isAISpeaking ? { scale: [1, 1.1, 1] } : {}}
                  transition={{ duration: 0.5, repeat: isAISpeaking ? Infinity : 0 }}
                  className="relative"
                >
                  <div className="w-32 h-32 rounded-full bg-gradient-to-r from-neon-blue to-neon-purple flex items-center justify-center">
                    <Brain className="w-16 h-16 text-white" />
                  </div>
                  {isAISpeaking && (
                    <motion.div
                      className="absolute -bottom-2 left-1/2 transform -translate-x-1/2"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    >
                      <Volume2 className="w-6 h-6 text-neon-cyan" />
                    </motion.div>
                  )}
                </motion.div>
              </div>

              {/* Status */}
              <div className="mt-4 text-center">
                <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-glass-border">
                  <div className={`w-2 h-2 rounded-full ${
                    isAISpeaking ? 'bg-green-400 animate-pulse' : 
                    isListening ? 'bg-yellow-400 animate-pulse' : 
                    'bg-gray-400'
                  }`} />
                  <span className="text-sm">
                    {isAISpeaking ? 'AI Speaking' : 
                     isListening ? 'Listening...' : 
                     'Ready'}
                  </span>
                </div>
              </div>

              <div className="mt-5 space-y-3 rounded-2xl border border-white/10 bg-black/20 p-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Round</span>
                  <span className="text-neon-cyan">{getQuestionRound(currentQuestion)}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Category</span>
                  <span className="text-violet-200">{typeof currentQuestion === 'string' ? 'General' : currentQuestion.type || 'General'}</span>
                </div>
                <div>
                  <div className="mb-2 flex items-center justify-between text-sm">
                    <span className="text-gray-400">Progress</span>
                    <span className="text-white">{currentQuestionIndex + 1}/{activeQuestions.length}</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/10">
                    <motion.div
                      className="h-full rounded-full bg-gradient-to-r from-neon-blue to-neon-purple"
                      animate={{ width: `${((currentQuestionIndex + 1) / activeQuestions.length) * 100}%` }}
                      transition={{ duration: 0.4 }}
                    />
                  </div>
                </div>
              </div>

              {/* Sound Wave */}
              {isAISpeaking && (
                <div className="mt-4 flex justify-center space-x-1">
                  {[...Array(5)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="w-1 bg-neon-cyan rounded-full"
                      animate={{ height: [10, 30, 10] }}
                      transition={{
                        duration: 0.5,
                        repeat: Infinity,
                        delay: i * 0.1
                      }}
                      style={{ height: '20px' }}
                    />
                  ))}
                </div>
              )}
            </div>
          </motion.div>

          {/* Center - Question Display */}
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="lg:col-span-6"
          >
            <div className="glass-card p-8 rounded-2xl h-full flex flex-col min-h-0">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold">Question {currentQuestionIndex + 1} of {activeQuestions.length}</h3>
                <span className="px-3 py-1 rounded-full bg-neon-blue/20 text-neon-cyan text-sm border border-neon-blue/30">
                  {getQuestionRound(currentQuestion)}
                </span>
              </div>
              
              {/* Question */}
              <div className="flex-1 min-h-[170px] flex items-center justify-center">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={getQuestionText(currentQuestion)}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.5 }}
                    className="text-2xl md:text-3xl font-light text-center text-white"
                  >
                    {getQuestionText(currentQuestion) || "Click 'Start Interview' to begin"}
                  </motion.div>
                </AnimatePresence>
              </div>

              {/* Voice Chat Transcript */}
              <div className="mt-6 rounded-2xl border border-white/10 bg-black/20 overflow-hidden">
                <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
                  <div className="flex items-center space-x-2">
                    <MessageSquare className="w-4 h-4 text-neon-cyan" />
                    <span className="text-sm font-semibold text-white">Interview Chat</span>
                  </div>
                  <span className="rounded-full border border-neon-blue/30 bg-neon-blue/10 px-3 py-1 text-xs text-neon-cyan">
                    Voice only
                  </span>
                </div>

                <div className="max-h-56 min-h-[150px] overflow-y-auto px-4 py-4 space-y-3">
                  {chatMessages.length === 0 && !transcript ? (
                    <div className="h-full min-h-[112px] flex items-center justify-center text-center">
                      <p className="max-w-md text-sm leading-6 text-gray-500">
                        AI questions, your spoken responses, and evaluation notes will appear here during the interview.
                      </p>
                    </div>
                  ) : (
                    <>
                      {chatMessages.map((message) => {
                        const isUser = message.role === 'user'
                        return (
                          <motion.div
                            key={message.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
                          >
                            <div className={`max-w-[86%] rounded-2xl px-4 py-3 ${
                              isUser
                                ? 'bg-gradient-to-br from-neon-blue/25 to-neon-purple/25 border border-neon-blue/30'
                                : 'bg-white/[0.06] border border-white/10'
                            }`}>
                              <div className="mb-1 flex items-center justify-between gap-3">
                                <span className={`text-xs font-semibold ${isUser ? 'text-neon-cyan' : 'text-violet-200'}`}>
                                  {message.label || (isUser ? 'Candidate' : 'AI Interviewer')}
                                </span>
                                <span className="text-[11px] text-gray-500">{message.timestamp}</span>
                              </div>
                              <p className="text-sm leading-6 text-gray-100">{message.text}</p>
                            </div>
                          </motion.div>
                        )
                      })}

                      {transcript && isListening && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex justify-end"
                        >
                          <div className="max-w-[86%] rounded-2xl border border-neon-cyan/30 bg-neon-cyan/10 px-4 py-3">
                            <div className="mb-1 flex items-center justify-between gap-3">
                              <span className="text-xs font-semibold text-neon-cyan">Live transcript</span>
                              <span className="text-[11px] text-gray-500">{formatTime(timer)}</span>
                            </div>
                            <p className="text-sm leading-6 text-gray-100">{transcript}</p>
                          </div>
                        </motion.div>
                      )}
                    </>
                  )}
                  <div ref={chatEndRef} />
                </div>
              </div>

              {/* Audio Waveform */}
              {isListening && (
                <div className="mt-8">
                  <div className="flex items-center justify-center space-x-1 h-16">
                    {[...Array(20)].map((_, i) => (
                      <motion.div
                        key={i}
                        className="w-2 bg-gradient-to-t from-neon-blue to-neon-cyan rounded-full"
                        animate={{ 
                          height: [10, audioLevel * 0.3 + 10, 10] 
                        }}
                        transition={{
                          duration: 0.1,
                          repeat: Infinity,
                          delay: i * 0.05
                        }}
                        style={{ height: '20px' }}
                      />
                    ))}
                  </div>
                  <p className="text-center text-gray-400 text-sm mt-2">Listening to your response...</p>
                </div>
              )}

              {/* Transcript */}
              {transcript && (
                <div className="mt-6 p-4 rounded-xl bg-glass-border">
                  <div className="flex items-center space-x-2 mb-2">
                    <MessageSquare className="w-4 h-4 text-neon-cyan" />
                    <span className="text-sm text-gray-400">Your Response</span>
                  </div>
                  <p className="text-white">{transcript}</p>
                </div>
              )}

              {currentQuestion && typeof currentQuestion !== 'string' && (
                <div className="mt-4 flex flex-wrap gap-2 justify-center">
                  <span className="px-3 py-1 rounded-full bg-glass-border text-xs text-gray-300">
                    {currentQuestion.difficulty}
                  </span>
                  <span className="px-3 py-1 rounded-full bg-glass-border text-xs text-gray-300">
                    Source: {currentQuestion.source}
                  </span>
                </div>
              )}

              {/* Answer Mode Toggle */}
              <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                <div className="mb-3 flex items-center justify-between gap-4">
                  <span className="text-sm font-semibold text-white">Answer Mode</span>
                  <span className="text-xs text-gray-500">Switch anytime before answering</span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setAnswerMode('voice')}
                    className={`flex items-center justify-center rounded-xl border px-4 py-3 text-sm font-semibold transition-all ${
                      answerMode === 'voice'
                        ? 'border-neon-blue/50 bg-neon-blue/20 text-neon-cyan shadow-[0_0_24px_rgba(0,212,255,.18)]'
                        : 'border-white/10 bg-black/20 text-gray-400 hover:text-white'
                    }`}
                  >
                    <Mic className="mr-2 h-4 w-4" />
                    Voice
                  </button>
                  <button
                    onClick={() => setAnswerMode('text')}
                    className={`flex items-center justify-center rounded-xl border px-4 py-3 text-sm font-semibold transition-all ${
                      answerMode === 'text'
                        ? 'border-neon-purple/50 bg-neon-purple/20 text-violet-200 shadow-[0_0_24px_rgba(124,58,237,.22)]'
                        : 'border-white/10 bg-black/20 text-gray-400 hover:text-white'
                    }`}
                  >
                    <Keyboard className="mr-2 h-4 w-4" />
                    Text
                  </button>
                </div>
              </div>

              {answerMode === 'text' && isInterviewActive && (
                <motion.div
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 rounded-2xl border border-neon-purple/25 bg-black/25 p-4 shadow-[0_0_28px_rgba(124,58,237,.12)]"
                >
                  <div className="mb-3 flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-sm font-semibold text-violet-200">
                      <MessageSquare className="h-4 w-4" />
                      <span>Text Answer</span>
                    </div>
                    {typedAnswer && (
                      <span className="text-xs text-neon-cyan">Typing...</span>
                    )}
                  </div>
                  <div className="flex gap-3">
                    <textarea
                      value={typedAnswer}
                      onChange={(event) => setTypedAnswer(event.target.value)}
                      onKeyDown={handleTextKeyDown}
                      disabled={isAISpeaking || isEvaluating}
                      rows={3}
                      className="min-h-[86px] flex-1 resize-none rounded-xl border border-white/10 bg-white/[0.06] px-4 py-3 text-sm leading-6 text-white placeholder-gray-500 outline-none transition focus:border-neon-purple/60 focus:shadow-[0_0_24px_rgba(124,58,237,.18)] disabled:opacity-60"
                      placeholder="Type your interview answer here..."
                    />
                    <button
                      onClick={submitTypedAnswer}
                      disabled={!typedAnswer.trim() || isAISpeaking || isEvaluating}
                      className="self-stretch rounded-xl border border-neon-blue/40 bg-gradient-to-br from-neon-blue to-neon-purple px-4 text-white shadow-[0_0_24px_rgba(0,212,255,.22)] transition hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-50"
                      aria-label="Send typed answer"
                    >
                      <Send className="h-5 w-5" />
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Control Buttons */}
              <div className="mt-8 flex justify-center space-x-4">
                {!isInterviewActive ? (
                  <button
                    onClick={startInterview}
                    className="btn-primary flex items-center"
                  >
                    <PlayCircle className="w-5 h-5 mr-2" />
                    Start Interview
                  </button>
                ) : (
                  <>
                    {answerMode === 'voice' && (
                      <button
                        onClick={nextQuestion}
                        disabled={isAISpeaking || isEvaluating}
                        className="btn-secondary flex items-center disabled:opacity-50"
                      >
                        {isEvaluating ? 'Evaluating...' : 'Next Question'}
                        <MessageSquare className="w-5 h-5 ml-2" />
                      </button>
                    )}
                    <button
                      onClick={endInterview}
                      disabled={isEvaluating}
                      className="px-6 py-3 rounded-xl bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 transition-colors flex items-center"
                    >
                      <StopCircle className="w-5 h-5 mr-2" />
                      End Interview
                    </button>
                  </>
                )}
              </div>
            </div>
          </motion.div>

          {/* Right Side - Webcam & Metrics */}
          <motion.div
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="lg:col-span-3"
          >
            <div className="glass-card p-6 rounded-2xl h-full flex flex-col">
              <h3 className="text-lg font-semibold mb-4 text-center">Behavior Tracking</h3>
              
              {/* Webcam Feed */}
              <div className="relative mb-4">
                <div className="aspect-video bg-dark-surface rounded-xl overflow-hidden relative">
                  {isCameraOn ? (
                    <>
                      <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        className="w-full h-full object-cover"
                      />
                      {/* Face Detection Box */}
                      {faceDetected && (
                        <motion.div
                          className="absolute top-1/4 left-1/4 w-1/2 h-1/2 border-2 border-green-400 rounded-lg"
                          animate={{ opacity: [0.5, 1, 0.5] }}
                          transition={{ duration: 2, repeat: Infinity }}
                        >
                          <div className="absolute -top-6 left-0 text-green-400 text-xs">
                            <Eye className="w-4 h-4 inline mr-1" />
                            Face Detected
                          </div>
                        </motion.div>
                      )}
                    </>
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Camera className="w-12 h-12 text-gray-500" />
                    </div>
                  )}
                </div>
              </div>

              {/* Behavior Metrics */}
              <div className="space-y-3">
                <div className="glass-card p-3 rounded-xl">
                  <div className="text-sm text-gray-400 mb-1">Camera State</div>
                  <div className={`font-semibold ${
                    !isCameraOn ? 'text-red-400' : faceDetected ? 'text-green-400' : 'text-yellow-400'
                  }`}>
                    {behaviorState}
                  </div>
                </div>
                <div className="glass-card p-3 rounded-xl">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-400 flex items-center">
                      <Eye className="w-4 h-4 mr-1" />
                      Eye Contact
                    </span>
                    <span className="text-sm font-semibold text-neon-cyan">{eyeContact}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <motion.div
                      className="bg-gradient-to-r from-neon-blue to-neon-cyan h-2 rounded-full"
                      animate={{ width: `${eyeContact}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>

                <div className="glass-card p-3 rounded-xl">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-400 flex items-center">
                      <Activity className="w-4 h-4 mr-1" />
                      Attention
                    </span>
                    <span className="text-sm font-semibold text-neon-cyan">{attention}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <motion.div
                      className="bg-gradient-to-r from-neon-purple to-neon-cyan h-2 rounded-full"
                      animate={{ width: `${attention}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>
              </div>

              {/* Control Buttons */}
              <div className="mt-auto pt-4 flex justify-center space-x-3">
                <button
                  onClick={toggleMic}
                  disabled={answerMode === 'text'}
                  className={`p-3 rounded-xl transition-all ${
                    answerMode === 'text'
                      ? 'bg-gray-500/10 text-gray-500 border border-white/10 cursor-not-allowed'
                      : isMicOn 
                      ? 'bg-neon-blue/20 text-neon-blue border border-neon-blue/30' 
                      : 'bg-red-500/20 text-red-400 border border-red-500/30'
                  }`}
                >
                  {isMicOn ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
                </button>
                <button
                  onClick={toggleCamera}
                  className={`p-3 rounded-xl transition-all ${
                    isCameraOn 
                      ? 'bg-neon-blue/20 text-neon-blue border border-neon-blue/30' 
                      : 'bg-red-500/20 text-red-400 border border-red-500/30'
                  }`}
                >
                  {isCameraOn ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default InterviewRoom
