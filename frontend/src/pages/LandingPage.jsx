import React from 'react'
import { motion } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import {
  ArrowRight,
  BarChart3,
  Brain,
  Briefcase,
  Building2,
  Camera,
  CheckCircle,
  FileText,
  LineChart,
  MessageSquare,
  Mic,
  PieChart,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  Users
} from 'lucide-react'

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0 }
}

const LandingPage = () => {
  const navigate = useNavigate()
  const stats = [
    { value: '10K+', label: 'Interview Sessions' },
    { value: '5K+', label: 'Students Practicing' },
    { value: '92%', label: 'Confidence Improvement' },
    { value: 'Ready', label: 'Institution Platform' }
  ]

  const features = [
    {
      icon: Brain,
      title: 'AI Interview Simulation',
      description: 'Role-specific mock interviews guided by adaptive AI questioning.'
    },
    {
      icon: FileText,
      title: 'Resume Intelligence',
      description: 'Resume-aware interview prompts built around skills, projects, and experience.'
    },
    {
      icon: Camera,
      title: 'Behavioral Analytics',
      description: 'Attention, eye contact, and engagement signals for interview readiness.'
    },
    {
      icon: MessageSquare,
      title: 'Voice & Chat Interviews',
      description: 'Flexible answer modes while keeping one consistent evaluation flow.'
    },
    {
      icon: Target,
      title: 'Real-Time Feedback',
      description: 'Clear strengths, gaps, and improvement notes after every response.'
    },
    {
      icon: BarChart3,
      title: 'Performance Dashboard',
      description: 'Professional analytics for candidates, mentors, and placement teams.'
    }
  ]

  const workflow = [
    'Upload Resume',
    'Select Role & Company',
    'AI Conducts Interview',
    'Get Evaluated',
    'Improve & Track'
  ]

  const clearPreviousSession = () => {
    const keysToClear = [
      'userId',
      'candidateName',
      'candidateEmail',
      'candidateProfile',
      'currentInterviewId',
      'currentReportId',
      'currentSessionId',
      'interviewReport',
      'interviewSession',
      'resumeAnalysis',
      'jobInsights',
      'selectedResume',
      'selectedJob'
    ]

    keysToClear.forEach((key) => {
      localStorage.removeItem(key)
      sessionStorage.removeItem(key)
    })

    Object.keys(sessionStorage)
      .filter((key) => key.startsWith('reportEmailAutomation:'))
      .forEach((key) => sessionStorage.removeItem(key))

    console.log('Previous session cleared')
  }

  const startFreshInterview = (event) => {
    event.preventDefault()
    clearPreviousSession()
    navigate('/profile')
  }

  return (
    <div className="min-h-screen overflow-hidden bg-dark-bg text-white">
      <div className="fixed inset-0 bg-[radial-gradient(circle_at_18%_4%,rgba(0,212,255,0.12),transparent_30%),radial-gradient(circle_at_88%_12%,rgba(124,58,237,0.12),transparent_28%),linear-gradient(135deg,#080912_0%,#101225_50%,#080912_100%)]" />
      <div className="fixed inset-0 opacity-[0.045] [background-image:linear-gradient(rgba(255,255,255,.35)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.35)_1px,transparent_1px)] [background-size:56px_56px]" />

      <nav className="sticky top-0 z-50 border-b border-white/10 bg-[#080912]/75 backdrop-blur-2xl">
        <div className="container mx-auto flex items-center justify-between px-4 py-4">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-neon-blue/25 bg-neon-blue/10">
              <Brain className="h-5 w-5 text-neon-cyan" />
            </div>
            <span className="text-xl font-bold tracking-tight">HireReady AI</span>
          </Link>

          <div className="hidden items-center gap-7 text-sm text-gray-300 lg:flex">
            <a href="#features" className="transition hover:text-white">Features</a>
            <a href="#how-it-works" className="transition hover:text-white">How It Works</a>
            <Link to="/dashboard" className="transition hover:text-white">Dashboard</Link>
            <a href="#institutions" className="transition hover:text-white">Institutions</a>
            <a href="#pricing" className="transition hover:text-white">Pricing</a>
          </div>

          <div className="flex items-center gap-3">
            <Link to="/profile" onClick={startFreshInterview} className="rounded-xl bg-gradient-to-r from-neon-blue to-neon-purple px-5 py-3 text-sm font-semibold text-white shadow-[0_0_20px_rgba(0,212,255,.16)] transition hover:shadow-[0_0_28px_rgba(0,212,255,.24)]">
              Start Interview
            </Link>
          </div>
        </div>
      </nav>

      <main className="relative z-10">
        <section className="container mx-auto grid items-center gap-12 px-4 pb-20 pt-20 lg:grid-cols-[1fr_.95fr] lg:pb-28 lg:pt-24">
          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            transition={{ duration: 0.65 }}
          >
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-neon-cyan">
              <ShieldCheck className="h-4 w-4" />
              AI interview readiness for candidates and institutions
            </div>
            <h1 className="max-w-4xl text-4xl font-semibold leading-tight tracking-tight text-white md:text-6xl">
              Prepare for real interviews with an AI platform built for measurable hiring readiness.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-gray-300">
              HireReady AI combines resume intelligence, adaptive mock interviews, behavior tracking, and performance analytics in one professional coaching workflow.
            </p>
            <div className="mt-9 flex flex-col gap-4 sm:flex-row">
              <Link to="/profile" onClick={startFreshInterview} className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-neon-blue to-neon-purple px-6 py-4 font-semibold text-white shadow-[0_0_24px_rgba(0,212,255,.18)] transition hover:-translate-y-0.5">
                Start Free Interview
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link to="/dashboard" className="inline-flex items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] px-6 py-4 font-semibold text-gray-200 backdrop-blur-xl transition hover:border-neon-blue/30 hover:text-white">
                Explore Platform
              </Link>
            </div>
            <div className="mt-8 flex flex-wrap items-center gap-5 text-sm text-gray-400">
              <span className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-neon-cyan" /> Resume-aware</span>
              <span className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-neon-cyan" /> Voice and chat</span>
              <span className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-neon-cyan" /> Analytics-ready</span>
            </div>
          </motion.div>

          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            transition={{ duration: 0.65, delay: 0.12 }}
            className="relative"
          >
            <div className="rounded-3xl border border-white/10 bg-white/[0.055] p-5 shadow-[0_24px_90px_rgba(0,0,0,.34)] backdrop-blur-2xl">
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Interview Analytics</p>
                  <h3 className="text-xl font-semibold text-white">Candidate Readiness Report</h3>
                </div>
                <div className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-sm text-emerald-300">
                  Live
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                {[
                  ['Overall', '84%', TrendingUp],
                  ['Technical', '76%', LineChart],
                  ['Behavior', '91%', Camera]
                ].map(([label, value, Icon]) => (
                  <div key={label} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                    <Icon className="mb-4 h-5 w-5 text-neon-cyan" />
                    <div className="text-2xl font-bold text-white">{value}</div>
                    <div className="mt-1 text-sm text-gray-400">{label}</div>
                  </div>
                ))}
              </div>

              <div className="mt-4 grid gap-4 lg:grid-cols-[.9fr_1.1fr]">
                <div className="rounded-2xl border border-white/10 bg-black/20 p-5">
                  <div className="mb-5 flex items-center justify-between">
                    <span className="text-sm text-gray-400">Competency Radar</span>
                    <PieChart className="h-4 w-4 text-violet-300" />
                  </div>
                  <div className="relative mx-auto flex h-44 w-44 items-center justify-center rounded-full border border-neon-blue/20 bg-neon-blue/5">
                    <div className="absolute h-32 w-32 rounded-full border border-violet-400/25" />
                    <div className="absolute h-20 w-20 rounded-full border border-neon-cyan/30" />
                    <div className="h-24 w-24 rounded-[36%_64%_48%_52%] bg-gradient-to-br from-neon-blue/65 to-neon-purple/65 opacity-90" />
                  </div>
                </div>

                <div className="rounded-2xl border border-white/10 bg-black/20 p-5">
                  <div className="mb-5 flex items-center justify-between">
                    <span className="text-sm text-gray-400">Question Performance</span>
                    <BarChart3 className="h-4 w-4 text-neon-cyan" />
                  </div>
                  <div className="flex h-44 items-end gap-3">
                    {[62, 78, 71, 88, 84].map((height, index) => (
                      <div key={index} className="flex flex-1 flex-col items-center gap-2">
                        <div className="w-full rounded-t-xl bg-gradient-to-t from-neon-purple/70 to-neon-blue/80" style={{ height: `${height}%` }} />
                        <span className="text-xs text-gray-500">Q{index + 1}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </section>

        <section className="container mx-auto px-4 py-10">
          <div className="grid gap-4 md:grid-cols-4">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                transition={{ duration: 0.45, delay: index * 0.05 }}
                className="rounded-2xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur-xl"
              >
                <div className="text-3xl font-semibold text-white">{stat.value}</div>
                <div className="mt-2 text-sm text-gray-400">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </section>

        <section id="features" className="container mx-auto px-4 py-20">
          <SectionHeader
            eyebrow="Platform capabilities"
            title="Everything needed to measure and improve interview readiness."
            description="A focused AI workflow for candidates, placement teams, and training institutions."
          />
          <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={feature.title}
                  variants={fadeUp}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  transition={{ duration: 0.45, delay: index * 0.04 }}
                  className="rounded-2xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur-xl transition hover:border-neon-blue/25 hover:bg-white/[0.06]"
                >
                  <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl border border-neon-blue/20 bg-neon-blue/10 text-neon-cyan">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
                  <p className="mt-3 leading-7 text-gray-400">{feature.description}</p>
                </motion.div>
              )
            })}
          </div>
        </section>

        <section id="how-it-works" className="container mx-auto px-4 py-20">
          <SectionHeader
            eyebrow="How it works"
            title="A structured readiness workflow from resume to report."
            description="Simple enough for students, rigorous enough for institutional review."
          />
          <div className="mt-12 grid gap-4 lg:grid-cols-5">
            {workflow.map((step, index) => (
              <motion.div
                key={step}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                transition={{ duration: 0.45, delay: index * 0.06 }}
                className="relative rounded-2xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur-xl"
              >
                <div className="mb-5 flex h-10 w-10 items-center justify-center rounded-full bg-neon-blue/10 text-sm font-semibold text-neon-cyan">
                  {index + 1}
                </div>
                <h3 className="text-base font-semibold text-white">{step}</h3>
                <p className="mt-3 text-sm leading-6 text-gray-400">
                  {[
                    'Parse skills, projects, education, and experience.',
                    'Align the session with a real hiring target.',
                    'Run adaptive questions in voice or text mode.',
                    'Score responses with feedback and missing points.',
                    'Use analytics to improve over repeat sessions.'
                  ][index]}
                </p>
              </motion.div>
            ))}
          </div>
        </section>

        <section id="institutions" className="container mx-auto px-4 py-20">
          <div className="grid items-center gap-10 rounded-3xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-2xl md:p-10 lg:grid-cols-[.85fr_1.15fr]">
            <div>
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/10 bg-black/20 px-4 py-2 text-sm text-neon-cyan">
                <Building2 className="h-4 w-4" />
                Analytics preview
              </div>
              <h2 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
                Recruiter-focused insights without a complicated review process.
              </h2>
              <p className="mt-5 leading-8 text-gray-300">
                Surface readiness scores, behavior patterns, answer quality, and improvement paths in a format that feels credible for business reviews and placement programs.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              {[
                ['Communication', '82%', 'Clear delivery with structured examples.'],
                ['Role Fit', '78%', 'Strong project alignment, API depth needs work.'],
                ['Behavior', '89%', 'High attention and consistent presence.'],
                ['Readiness', 'Hire', 'Candidate is ready for guided interview loops.']
              ].map(([label, value, note]) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-black/20 p-5">
                  <div className="text-sm text-gray-400">{label}</div>
                  <div className="mt-3 text-3xl font-semibold text-white">{value}</div>
                  <p className="mt-3 text-sm leading-6 text-gray-400">{note}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="pricing" className="container mx-auto px-4 py-20">
          <motion.div
            variants={fadeUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            transition={{ duration: 0.55 }}
            className="rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.07] to-white/[0.035] p-8 text-center backdrop-blur-2xl md:p-12"
          >
            <Briefcase className="mx-auto mb-5 h-12 w-12 text-neon-cyan" />
            <h2 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
              Start Preparing for Real Interviews with AI
            </h2>
            <p className="mx-auto mt-5 max-w-2xl leading-8 text-gray-300">
              Practice with realistic questions, receive structured feedback, and track progress with professional analytics.
            </p>
            <div className="mt-8 flex flex-col justify-center gap-4 sm:flex-row">
              <Link to="/profile" onClick={startFreshInterview} className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-neon-blue to-neon-purple px-6 py-4 font-semibold text-white shadow-[0_0_24px_rgba(0,212,255,.18)]">
                Start Free Interview
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link to="/dashboard" className="inline-flex items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] px-6 py-4 font-semibold text-gray-200 transition hover:border-neon-blue/30 hover:text-white">
                Explore Platform
              </Link>
            </div>
          </motion.div>
        </section>
      </main>
    </div>
  )
}

const SectionHeader = ({ eyebrow, title, description }) => (
  <motion.div
    variants={fadeUp}
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true }}
    transition={{ duration: 0.5 }}
    className="mx-auto max-w-3xl text-center"
  >
    <p className="text-sm font-medium uppercase tracking-[0.24em] text-neon-cyan">{eyebrow}</p>
    <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white md:text-4xl">{title}</h2>
    <p className="mt-4 text-lg leading-8 text-gray-400">{description}</p>
  </motion.div>
)

export default LandingPage
