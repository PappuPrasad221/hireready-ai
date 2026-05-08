import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Briefcase, Mail, Shield, User } from 'lucide-react'
import apiService from '../api/api'

const initialForm = {
  fullName: '',
  email: '',
  phone: '',
  institution: '',
  branch: '',
  targetRole: ''
}

const createNewCandidateSession = (profile) => {
  const currentProfile = {
    ...profile,
    userId: profile.userId,
    sessionId: profile.sessionId
  }

  localStorage.setItem('candidateProfile', JSON.stringify(currentProfile))
  sessionStorage.setItem('candidateProfile', JSON.stringify(currentProfile))
  localStorage.setItem('userId', currentProfile.userId || '')
  sessionStorage.setItem('userId', currentProfile.userId || '')
  localStorage.setItem('candidateName', currentProfile.fullName || '')
  sessionStorage.setItem('candidateName', currentProfile.fullName || '')
  localStorage.setItem('candidateEmail', currentProfile.email || '')
  sessionStorage.setItem('candidateEmail', currentProfile.email || '')
  localStorage.setItem('currentSessionId', currentProfile.sessionId || '')
  sessionStorage.setItem('currentSessionId', currentProfile.sessionId || '')

  console.log('New candidate profile saved')
  console.log('Current userId', currentProfile.userId)
  console.log('Current candidateEmail', currentProfile.email)

  return currentProfile
}

const ProfileCapture = () => {
  const navigate = useNavigate()
  const [form, setForm] = useState(initialForm)
  const [error, setError] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  const updateField = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (!form.fullName.trim()) {
      setError('Please enter your full name.')
      return
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
      setError('Please enter a valid email address.')
      return
    }

    setIsSaving(true)
    try {
      const response = await apiService.saveCandidateProfile(form)
      const profile = response.profile || response.user || { ...form }
      createNewCandidateSession(profile)
      navigate('/resume')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Could not save your profile. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-dark-bg text-white">
      <div className="fixed inset-0 bg-gradient-to-br from-slate-950 via-dark-surface to-slate-950" />
      <div className="fixed inset-0 opacity-30">
        <div className="absolute left-1/4 top-20 h-72 w-72 rounded-full bg-neon-blue/20 blur-3xl" />
        <div className="absolute right-1/4 bottom-20 h-80 w-80 rounded-full bg-neon-purple/15 blur-3xl" />
      </div>

      <main className="relative z-10 flex min-h-screen items-center justify-center px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
          className="grid w-full max-w-6xl gap-8 lg:grid-cols-[0.9fr_1.1fr]"
        >
          <section className="hidden lg:flex flex-col justify-between rounded-3xl border border-white/10 bg-white/[0.04] p-8 shadow-2xl backdrop-blur-xl">
            <div>
              <div className="mb-8 inline-flex items-center gap-3 rounded-full border border-neon-blue/30 bg-neon-blue/10 px-4 py-2 text-sm text-neon-cyan">
                <Shield className="h-4 w-4" />
                Secure report delivery
              </div>
              <h1 className="mb-5 text-4xl font-bold leading-tight">
                Tell us where to send your interview report.
              </h1>
              <p className="text-lg leading-8 text-gray-300">
                HireReady AI uses this profile to personalize your interview session and automatically email your final PDF report after completion.
              </p>
            </div>

            <div className="grid gap-4">
              {[
                ['Profile capture', 'Name and email before interview prep'],
                ['PDF export', 'Professional report generated after completion'],
                ['Email automation', 'Brevo first, Resend backup if needed']
              ].map(([title, detail]) => (
                <div key={title} className="rounded-2xl border border-white/10 bg-slate-900/60 p-4">
                  <p className="font-semibold text-white">{title}</p>
                  <p className="mt-1 text-sm text-gray-400">{detail}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-white/[0.06] p-6 shadow-2xl backdrop-blur-xl sm:p-8">
            <div className="mb-8">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-neon-blue to-neon-purple">
                <User className="h-6 w-6" />
              </div>
              <h2 className="text-3xl font-bold">Candidate Profile</h2>
              <p className="mt-2 text-gray-400">Required before starting your AI interview workflow.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid gap-5 md:grid-cols-2">
                <label className="block">
                  <span className="mb-2 block text-sm text-gray-300">Full Name *</span>
                  <input
                    value={form.fullName}
                    onChange={(event) => updateField('fullName', event.target.value)}
                    className="w-full rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-white outline-none transition focus:border-neon-blue/70 focus:ring-2 focus:ring-neon-blue/20"
                    placeholder="Your full name"
                  />
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm text-gray-300">Email *</span>
                  <input
                    value={form.email}
                    onChange={(event) => updateField('email', event.target.value)}
                    className="w-full rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-white outline-none transition focus:border-neon-blue/70 focus:ring-2 focus:ring-neon-blue/20"
                    placeholder="name@example.com"
                    type="email"
                  />
                </label>
              </div>

              <div className="grid gap-5 md:grid-cols-2">
                <label className="block">
                  <span className="mb-2 block text-sm text-gray-300">Phone Number</span>
                  <input
                    value={form.phone}
                    onChange={(event) => updateField('phone', event.target.value)}
                    className="w-full rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-white outline-none transition focus:border-neon-blue/70 focus:ring-2 focus:ring-neon-blue/20"
                    placeholder="Optional"
                  />
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm text-gray-300">Target Role</span>
                  <input
                    value={form.targetRole}
                    onChange={(event) => updateField('targetRole', event.target.value)}
                    className="w-full rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-white outline-none transition focus:border-neon-blue/70 focus:ring-2 focus:ring-neon-blue/20"
                    placeholder="AI Engineer, Frontend Developer..."
                  />
                </label>
              </div>

              <label className="block">
                <span className="mb-2 block text-sm text-gray-300">College / Institution</span>
                <input
                  value={form.institution}
                  onChange={(event) => updateField('institution', event.target.value)}
                  className="w-full rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-white outline-none transition focus:border-neon-blue/70 focus:ring-2 focus:ring-neon-blue/20"
                  placeholder="Your college or institution"
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm text-gray-300">Branch / Department</span>
                <input
                  value={form.branch}
                  onChange={(event) => updateField('branch', event.target.value)}
                  className="w-full rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-white outline-none transition focus:border-neon-blue/70 focus:ring-2 focus:ring-neon-blue/20"
                  placeholder="Computer Science, AI & ML..."
                />
              </label>

              {error && (
                <div className="rounded-2xl border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isSaving}
                className="btn-primary w-full justify-center text-base disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSaving ? 'Saving Profile...' : 'Continue to Interview'}
                <ArrowRight className="ml-2 h-5 w-5" />
              </button>

              <button
                type="button"
                disabled
                className="flex w-full items-center justify-center rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-gray-500"
              >
                <Mail className="mr-2 h-4 w-4" />
                Google login placeholder
              </button>

              <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                <Briefcase className="h-4 w-4" />
                Used only for report delivery and interview personalization.
              </div>
            </form>
          </section>
        </motion.div>
      </main>
    </div>
  )
}

export default ProfileCapture
