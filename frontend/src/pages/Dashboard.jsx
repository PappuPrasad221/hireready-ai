import React, { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { Link, useLocation } from 'react-router-dom'
import {
  Activity,
  ArrowRight,
  Brain,
  Briefcase,
  Calendar,
  Clock,
  Download,
  RefreshCw,
  Sparkles,
  User
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts'
import ScoreCard from '../components/dashboard/ScoreCard'
import RadarAnalytics from '../components/dashboard/RadarAnalytics'
import QuestionAnalysisCard from '../components/dashboard/QuestionAnalysisCard'
import BehaviorPanel from '../components/dashboard/BehaviorPanel'
import VoiceAnalytics from '../components/dashboard/VoiceAnalytics'
import ReplayTimeline from '../components/dashboard/ReplayTimeline'
import DeepExplanationModal from '../components/dashboard/DeepExplanationModal'
import RecommendationPanel from '../components/dashboard/RecommendationPanel'

const safeParse = (key, fallback = {}) => {
  try {
    return JSON.parse(sessionStorage.getItem(key) || JSON.stringify(fallback))
  } catch {
    return fallback
  }
}

const asScore = (value) => {
  const parsed = Number(value)
  if (!Number.isFinite(parsed)) return null
  return Math.max(0, Math.min(100, Math.round(parsed)))
}

const average = (values) => {
  const valid = values.map(asScore).filter((value) => value !== null)
  if (!valid.length) return null
  return Math.round(valid.reduce((sum, value) => sum + value, 0) / valid.length)
}

const getQuestionText = (question) => {
  if (!question) return 'Question not captured'
  return typeof question === 'string' ? question : question.question || 'Question not captured'
}

const getRoundName = (question) => {
  if (!question || typeof question === 'string') return 'General'
  return question.round || question.type || 'General'
}

const normalizeList = (value) => {
  if (!value) return []
  if (Array.isArray(value)) return value.filter(Boolean)
  return [value]
}

const buildDashboardModel = (report, interviewState, resumeAnalysis) => {
  const categoryScores = report.category_scores || {}
  const roundScores = report.round_wise_scores || {}
  const replay = Array.isArray(report.replay_timeline) ? report.replay_timeline : []
  const questionRows = replay.map((item, index) => {
    const overall =
      item.score ??
      item.scores?.overall ??
      item.feedback?.scores?.overall ??
      item.evaluation?.scores?.overall

    return {
      id: `${index}-${getQuestionText(item.question).slice(0, 18)}`,
      index: index + 1,
      question: item.question,
      questionText: getQuestionText(item.question),
      answer: item.answer || item.transcript || 'Answer transcript not captured.',
      round: item.round || getRoundName(item.question),
      timestamp: item.timestamp || item.time || null,
      score: asScore(overall),
      feedback: item.feedback || item.evaluation?.feedback || {},
      behaviorData: item.behavior_data || item.behaviorData || {}
    }
  })

  const technical = asScore(categoryScores.technical)
  const communication = asScore(categoryScores.communication)
  const confidence = asScore(categoryScores.confidence)
  const behavior = asScore(categoryScores.behavior)
  const clarity = asScore(categoryScores.clarity) ?? communication
  const structure = asScore(categoryScores.structure) ?? asScore(categoryScores.completeness)
  const problemSolving =
    asScore(categoryScores.problem_solving) ??
    asScore(categoryScores.problemSolving) ??
    asScore(roundScores.Technical) ??
    technical
  const relevance =
    asScore(categoryScores.relevance) ??
    average(questionRows.map((item) => item.feedback?.scores?.relevance)) ??
    average(questionRows.map((item) => item.score))

  const scoreCards = [
    {
      label: 'Technical Score',
      score: technical,
      insight: technical === null ? 'Technical scoring was not returned by the evaluation.' : 'Measures depth, correctness, and role fit.'
    },
    {
      label: 'Communication Score',
      score: communication,
      insight: communication === null ? 'Communication scoring was not captured.' : 'Measures clarity, pacing, and answer delivery.'
    },
    {
      label: 'Confidence Score',
      score: confidence,
      insight: confidence === null ? 'Confidence scoring was not captured.' : 'Measures certainty, ownership, and fluency.'
    },
    {
      label: 'Behavior Score',
      score: behavior,
      insight: behavior === null ? 'Behavior tracking did not return a score.' : 'Uses camera attention signals where available.'
    },
    {
      label: 'Problem Solving Score',
      score: problemSolving,
      insight: problemSolving === null ? 'Problem solving was not scored separately.' : 'Reflects approach, tradeoffs, and reasoning quality.'
    },
    {
      label: 'Relevance Score',
      score: relevance,
      insight: relevance === null ? 'Relevance was not scored separately.' : 'Shows how closely answers matched the asked questions.'
    }
  ]

  const radarData = [
    { subject: 'Technical', score: technical },
    { subject: 'Communication', score: communication },
    { subject: 'Confidence', score: confidence },
    { subject: 'Behavior', score: behavior },
    { subject: 'Clarity', score: clarity },
    { subject: 'Structure', score: structure }
  ].map((item) => ({ ...item, score: item.score ?? 0, captured: item.score !== null }))

  const chartRows = questionRows.map((item) => ({
    name: `Q${item.index}`,
    score: item.score ?? 0,
    round: item.round,
    captured: item.score !== null
  }))

  const behaviorSamples = questionRows.map((item) => item.behaviorData).filter(Boolean)
  const behaviorMetrics = {
    score: behavior,
    eyeContact: asScore(report.behavior_metrics?.eye_contact ?? average(behaviorSamples.map((item) => item.eye_contact))),
    attention: asScore(report.behavior_metrics?.attention ?? average(behaviorSamples.map((item) => item.attention))),
    faceVisibility: asScore(report.behavior_metrics?.face_visibility ?? average(behaviorSamples.map((item) => (item.face_detected ? 100 : 0)))),
    lookingAwayCount: report.behavior_metrics?.looking_away_count ?? behaviorSamples.filter((item) => item.behavior_state === 'Looking Away').length,
    distractionCount: report.behavior_metrics?.distraction_count ?? behaviorSamples.reduce((sum, item) => sum + Number(item.distraction_count || 0), 0),
    summary: report.behavior_summary || report.behavior_analysis || null
  }

  const voiceAnalytics = report.voice_analytics || {
    clarityScore: clarity,
    confidenceLevel: confidence,
    speakingSpeed: null,
    pauses: null,
    fillerWords: null
  }

  return {
    candidate: {
      name: resumeAnalysis.candidateName || resumeAnalysis.name || report.candidate_name || 'Candidate',
      role: report.role || interviewState.role || interviewState.targetRole || 'Target role not captured',
      company: report.company || interviewState.company || interviewState.targetCompany || 'Target company not captured',
      date: report.generated_at || report.interview_date || new Date().toISOString(),
      duration: report.duration || interviewState.duration || null
    },
    overallScore: asScore(report.overall_score ?? report.overallScore),
    summary:
      report.performance_summary ||
      report.summary ||
      report.ai_summary ||
      'AI summary was not included in the generated report.',
    scoreCards,
    radarData,
    chartRows,
    questionRows,
    behaviorMetrics,
    voiceAnalytics,
    insights: {
      strengths: normalizeList(report.strengths),
      weaknesses: normalizeList(report.weaknesses),
      missingSkills: normalizeList(report.missing_skills),
      communicationIssues: normalizeList(report.communication_issues),
      confidenceObservations: normalizeList(report.confidence_observations),
      behavioralObservations: normalizeList(report.behavioral_observations)
    },
    recommendation: {
      label: report.hiring_recommendation || report.final_recommendation || report.recommendation || null,
      roadmap: normalizeList(report.improvement_roadmap || report.recommendations || report.improvements),
      learningTopics: normalizeList(report.suggested_learning_topics || report.missing_skills),
      practiceAreas: normalizeList(report.practice_areas || report.next_steps)
    }
  }
}

const MetricPill = ({ icon: Icon, label, value }) => (
  <div className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3">
    <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-gray-500">
      <Icon className="h-4 w-4 text-neon-cyan" />
      {label}
    </div>
    <div className="mt-2 text-sm font-semibold text-white">{value}</div>
  </div>
)

const Dashboard = () => {
  const location = useLocation()
  const [activeExplanation, setActiveExplanation] = useState(null)
  const report = location.state?.report || safeParse('interviewReport', {})
  const interviewState = safeParse('interviewState', {})
  const resumeAnalysis = safeParse('resumeAnalysis', {})
  const hasReport = Boolean(report && Object.keys(report).length)

  const model = useMemo(
    () => (hasReport ? buildDashboardModel(report, interviewState, resumeAnalysis) : null),
    [hasReport, report, interviewState, resumeAnalysis]
  )

  if (!hasReport) {
    return (
      <div className="relative min-h-screen overflow-hidden bg-dark-bg">
        <div className="fixed inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(0,212,255,0.16),transparent_30%),radial-gradient(circle_at_80%_10%,rgba(124,58,237,0.20),transparent_34%),linear-gradient(135deg,#05060b_0%,#101225_55%,#070812_100%)]" />
        <div className="relative z-10 flex min-h-screen items-center justify-center px-6">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card max-w-2xl rounded-2xl p-8 text-center"
          >
            <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl border border-neon-blue/30 bg-neon-blue/10 neon-glow">
              <Brain className="h-8 w-8 text-neon-blue" />
            </div>
            <h1 className="text-3xl font-bold text-gradient">Interview Results Dashboard</h1>
            <p className="mt-4 text-gray-400">
              No completed interview report is available yet. Finish a voice interview to generate real scores, replay analytics, and AI feedback.
            </p>
            <Link to="/interview" className="btn-primary mt-8 inline-flex items-center">
              Start Interview
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </motion.div>
        </div>
      </div>
    )
  }

  const formattedDate = model.candidate.date
    ? new Date(model.candidate.date).toLocaleString()
    : 'Not captured'
  const duration = model.candidate.duration ? model.candidate.duration : 'Not captured'

  return (
    <div className="relative min-h-screen overflow-hidden bg-dark-bg">
      <div className="fixed inset-0 bg-[radial-gradient(circle_at_15%_12%,rgba(0,212,255,0.18),transparent_28%),radial-gradient(circle_at_82%_0%,rgba(124,58,237,0.24),transparent_32%),linear-gradient(135deg,#05060b_0%,#11142a_52%,#070812_100%)]" />
      <div className="fixed inset-0 opacity-[0.07] [background-image:linear-gradient(rgba(255,255,255,.45)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.45)_1px,transparent_1px)] [background-size:44px_44px]" />

      <nav className="relative z-10 mx-4 mt-4 rounded-2xl border border-white/10 bg-white/[0.04] px-6 py-4 backdrop-blur-2xl">
        <div className="container mx-auto flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-neon-blue to-neon-purple shadow-[0_0_34px_rgba(0,212,255,.35)]">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-neon-cyan">HireReady AI</p>
              <h1 className="text-xl font-bold text-white">Interview Results Dashboard</h1>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => window.location.reload()}
              className="rounded-xl border border-white/10 bg-white/[0.04] p-3 text-gray-300 transition hover:border-neon-blue/40 hover:text-white"
              aria-label="Refresh dashboard"
            >
              <RefreshCw className="h-5 w-5" />
            </button>
            <Link to="/" className="text-sm font-medium text-gray-300 transition hover:text-white">
              Home
            </Link>
          </div>
        </div>
      </nav>

      <main className="relative z-10 container mx-auto px-4 py-8">
        <section className="grid gap-6 xl:grid-cols-[1.35fr_.65fr]">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-2xl shadow-[0_24px_90px_rgba(0,0,0,.32)]"
          >
            <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-neon-blue/30 bg-neon-blue/10 px-4 py-2 text-sm text-neon-cyan">
                  <Sparkles className="h-4 w-4" />
                  AI performance report
                </div>
                <h2 className="text-3xl font-bold text-white md:text-5xl">
                  {model.candidate.name}
                </h2>
                <p className="mt-4 max-w-3xl text-lg leading-8 text-gray-300">
                  {model.summary}
                </p>
              </div>

              <div className="relative mx-auto flex h-48 w-48 shrink-0 items-center justify-center rounded-full">
                <motion.div
                  initial={{ rotate: -90 }}
                  animate={{ rotate: 0 }}
                  transition={{ duration: 1.1 }}
                  className="absolute inset-0 rounded-full"
                  style={{
                    background: `conic-gradient(#00d4ff ${model.overallScore || 0}%, rgba(255,255,255,.08) 0)`
                  }}
                />
                <div className="absolute inset-3 rounded-full bg-[#070812]" />
                <div className="relative text-center">
                  <div className="text-5xl font-black text-gradient">{model.overallScore ?? '--'}%</div>
                  <div className="mt-2 text-xs uppercase tracking-[0.24em] text-gray-500">Overall</div>
                </div>
              </div>
            </div>

            <div className="mt-8 grid gap-3 md:grid-cols-5">
              <MetricPill icon={User} label="Name" value={model.candidate.name} />
              <MetricPill icon={Briefcase} label="Role" value={model.candidate.role} />
              <MetricPill icon={Sparkles} label="Company" value={model.candidate.company} />
              <MetricPill icon={Calendar} label="Date" value={formattedDate} />
              <MetricPill icon={Clock} label="Duration" value={duration} />
            </div>
          </motion.div>

          <RecommendationPanel recommendation={model.recommendation} overallScore={model.overallScore} />
        </section>

        <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {model.scoreCards.map((card, index) => (
            <ScoreCard key={card.label} {...card} index={index} />
          ))}
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-2">
          <RadarAnalytics data={model.radarData} />
          <motion.div
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="rounded-2xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-2xl"
          >
            <h3 className="mb-6 text-xl font-semibold text-white">Question-wise Scores</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={model.chartRows}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.08)" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" domain={[0, 100]} />
                <Tooltip
                  cursor={{ fill: 'rgba(0,212,255,.08)' }}
                  contentStyle={{ background: '#101225', border: '1px solid rgba(255,255,255,.12)', borderRadius: 12 }}
                />
                <Bar dataKey="score" fill="url(#barGradient)" radius={[10, 10, 0, 0]} />
                <defs>
                  <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#00d4ff" />
                    <stop offset="100%" stopColor="#7c3aed" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        </section>

        <section className="mt-8 rounded-2xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-2xl">
          <h3 className="mb-6 text-xl font-semibold text-white">Performance Progression</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={model.chartRows}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.08)" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" domain={[0, 100]} />
              <Tooltip contentStyle={{ background: '#101225', border: '1px solid rgba(255,255,255,.12)', borderRadius: 12 }} />
              <Line type="monotone" dataKey="score" stroke="#00d4ff" strokeWidth={3} dot={{ r: 5, fill: '#7c3aed' }} />
            </LineChart>
          </ResponsiveContainer>
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-[.9fr_1.1fr]">
          <div className="space-y-6">
            <div className="rounded-2xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-2xl">
              <h3 className="mb-5 text-xl font-semibold text-white">AI Insights</h3>
              <div className="grid gap-4 md:grid-cols-2">
                {[
                  ['Strengths', model.insights.strengths, 'text-emerald-300'],
                  ['Weaknesses', model.insights.weaknesses, 'text-rose-300'],
                  ['Missing Skills', model.insights.missingSkills, 'text-amber-300'],
                  ['Communication', model.insights.communicationIssues, 'text-neon-cyan'],
                  ['Confidence', model.insights.confidenceObservations, 'text-violet-300'],
                  ['Behavior', model.insights.behavioralObservations, 'text-blue-300']
                ].map(([title, items, color]) => (
                  <div key={title} className="rounded-xl border border-white/10 bg-black/20 p-4">
                    <h4 className={`mb-3 text-sm font-semibold ${color}`}>{title}</h4>
                    {items.length ? (
                      <ul className="space-y-2 text-sm text-gray-300">
                        {items.map((item) => (
                          <li key={item} className="leading-6">{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-500">Not captured in this report.</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
            <BehaviorPanel metrics={model.behaviorMetrics} />
            <VoiceAnalytics analytics={model.voiceAnalytics} />
          </div>

          <div className="space-y-6">
            <div className="rounded-2xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-2xl">
              <h3 className="mb-5 text-xl font-semibold text-white">Question-wise Analysis</h3>
              <div className="space-y-4">
                {model.questionRows.length ? (
                  model.questionRows.map((item) => (
                    <QuestionAnalysisCard
                      key={item.id}
                      item={item}
                      onExplain={() => setActiveExplanation(item)}
                    />
                  ))
                ) : (
                  <p className="rounded-xl border border-white/10 bg-black/20 p-4 text-gray-400">
                    Question evaluations were not included in the report.
                  </p>
                )}
              </div>
            </div>
            <ReplayTimeline items={model.questionRows} />
          </div>
        </section>

        <section className="mt-8 flex flex-col justify-center gap-4 sm:flex-row">
          <Link to="/interview" className="btn-primary inline-flex items-center justify-center text-lg">
            Practice Again
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
          <button className="btn-secondary inline-flex items-center justify-center text-lg">
            <Download className="mr-2 h-5 w-5" />
            Export Report
          </button>
        </section>
      </main>

      <DeepExplanationModal item={activeExplanation} onClose={() => setActiveExplanation(null)} />
    </div>
  )
}

export default Dashboard
