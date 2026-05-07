import React from 'react'
import { HashRouter as Router, Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import LandingPage from './pages/LandingPage'
import ResumeUpload from './pages/ResumeUpload'
import InterviewSetup from './pages/InterviewSetup'
import InterviewRoom from './pages/InterviewRoom'
import FeedbackPanel from './pages/FeedbackPanel'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-dark-bg">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/resume" element={<ResumeUpload />} />
          <Route path="/setup" element={<InterviewSetup />} />
          <Route path="/interview" element={<InterviewRoom />} />
          <Route path="/feedback" element={<FeedbackPanel />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
