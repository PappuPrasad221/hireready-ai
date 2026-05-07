import React from 'react'
import { motion } from 'framer-motion'
import { Activity } from 'lucide-react'

const scoreTone = (score) => {
  if (score === null || score === undefined) return 'from-gray-500 to-gray-400'
  if (score >= 80) return 'from-emerald-400 to-neon-cyan'
  if (score >= 60) return 'from-amber-300 to-neon-blue'
  return 'from-rose-400 to-neon-purple'
}

const ScoreCard = ({ label, score, insight, index = 0 }) => {
  const captured = score !== null && score !== undefined

  return (
    <motion.div
      initial={{ opacity: 0, y: 22 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.45, delay: index * 0.05 }}
      whileHover={{ y: -4, scale: 1.01 }}
      className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.045] p-5 backdrop-blur-2xl transition hover:border-neon-blue/40 hover:shadow-[0_0_34px_rgba(0,212,255,.18)]"
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-neon-blue/70 to-transparent opacity-0 transition group-hover:opacity-100" />
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <div className="mt-3 flex items-end gap-2">
            <span className="text-4xl font-black text-white">{captured ? score : '--'}</span>
            <span className="pb-1 text-sm text-gray-500">%</span>
          </div>
        </div>
        <div className={`rounded-xl bg-gradient-to-br ${scoreTone(score)} p-3 shadow-[0_0_24px_rgba(0,212,255,.18)]`}>
          <Activity className="h-5 w-5 text-white" />
        </div>
      </div>
      <div className="mt-5 h-2 rounded-full bg-white/10">
        <motion.div
          className={`h-full rounded-full bg-gradient-to-r ${scoreTone(score)}`}
          initial={{ width: 0 }}
          whileInView={{ width: `${captured ? score : 0}%` }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.1 + index * 0.05 }}
        />
      </div>
      <p className="mt-4 min-h-[48px] text-sm leading-6 text-gray-400">{insight}</p>
    </motion.div>
  )
}

export default ScoreCard
