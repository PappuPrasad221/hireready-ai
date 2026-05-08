import React from 'react'
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import ResumeUpload from './pages/ResumeUpload'
import InterviewSetup from './pages/InterviewSetup'
import InterviewRoom from './pages/InterviewRoom'
import FeedbackPanel from './pages/FeedbackPanel'
import Dashboard from './pages/Dashboard'
import ProfileCapture from './pages/ProfileCapture'

const hasCandidateProfile = () => {
  return Boolean(localStorage.getItem('candidateProfile') || sessionStorage.getItem('candidateProfile'))
}

const RequireProfile = ({ children }) => {
  return hasCandidateProfile() ? children : <Navigate to="/profile" replace />
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-dark-bg">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/profile" element={<ProfileCapture />} />
          <Route path="/resume" element={<RequireProfile><ResumeUpload /></RequireProfile>} />
          <Route path="/setup" element={<RequireProfile><InterviewSetup /></RequireProfile>} />
          <Route path="/interview" element={<InterviewRoom />} />
          <Route path="/feedback" element={<FeedbackPanel />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
