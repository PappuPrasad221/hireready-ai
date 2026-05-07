import React from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, Eye, ScanFace } from 'lucide-react'

const Metric = ({ label, value }) => {
  const captured = value !== null && value !== undefined && value !== ''
  return (
    <div className="rounded-xl border border-white/10 bg-black/20 p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-gray-500">{label}</p>
      <div className="mt-3 text-2xl font-bold text-white">{captured ? value : 'Not captured'}</div>
    </div>
  )
}

const BehaviorPanel = ({ metrics }) => {
  const lowAttention = metrics.score !== null && metrics.score < 60

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="rounded-2xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-2xl"
    >
      <div className="mb-5 flex items-center justify-between">
        <h3 className="text-xl font-semibold text-white">Behavior Analytics</h3>
        <div className="rounded-xl border border-neon-blue/30 bg-neon-blue/10 p-2 text-neon-cyan">
          <ScanFace className="h-5 w-5" />
        </div>
      </div>
      {lowAttention && (
        <div className="mb-4 flex items-center gap-2 rounded-xl border border-amber-400/25 bg-amber-400/10 px-4 py-3 text-sm text-amber-200">
          <AlertTriangle className="h-4 w-4" />
          Low attention detected during interview.
        </div>
      )}
      <div className="grid gap-3 sm:grid-cols-2">
        <Metric label="Eye Contact" value={metrics.eyeContact !== null ? `${metrics.eyeContact}%` : null} />
        <Metric label="Attention" value={metrics.attention !== null ? `${metrics.attention}%` : null} />
        <Metric label="Face Visibility" value={metrics.faceVisibility !== null ? `${metrics.faceVisibility}%` : null} />
        <Metric label="Looking Away Count" value={metrics.lookingAwayCount} />
        <Metric label="Distraction Count" value={metrics.distractionCount} />
        <Metric label="Behavior Score" value={metrics.score !== null ? `${metrics.score}%` : null} />
      </div>
      <div className="mt-5 rounded-xl border border-neon-blue/20 bg-neon-blue/10 p-4">
        <div className="mb-2 flex items-center gap-2 text-neon-cyan">
          <Eye className="h-4 w-4" />
          <span className="text-sm font-semibold">AI behavior summary</span>
        </div>
        <p className="text-sm leading-6 text-gray-300">{metrics.summary || 'Behavior summary was not included in this report.'}</p>
      </div>
    </motion.div>
  )
}

export default BehaviorPanel
