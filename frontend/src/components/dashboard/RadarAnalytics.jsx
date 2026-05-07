import React from 'react'
import { motion } from 'framer-motion'
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip
} from 'recharts'
import { Target } from 'lucide-react'

const RadarAnalytics = ({ data }) => (
  <motion.div
    initial={{ opacity: 0, x: -24 }}
    whileInView={{ opacity: 1, x: 0 }}
    viewport={{ once: true }}
    className="rounded-2xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-2xl"
  >
    <div className="mb-6 flex items-center justify-between">
      <h3 className="text-xl font-semibold text-white">Competency Radar</h3>
      <div className="rounded-xl border border-neon-blue/30 bg-neon-blue/10 p-2 text-neon-cyan">
        <Target className="h-5 w-5" />
      </div>
    </div>
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data}>
        <PolarGrid stroke="rgba(255,255,255,.12)" />
        <PolarAngleAxis dataKey="subject" stroke="#cbd5e1" tick={{ fontSize: 12 }} />
        <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="rgba(255,255,255,.22)" tick={false} />
        <Radar
          name="Score"
          dataKey="score"
          stroke="#00d4ff"
          fill="#7c3aed"
          fillOpacity={0.42}
          strokeWidth={3}
        />
        <Tooltip
          contentStyle={{ background: '#101225', border: '1px solid rgba(255,255,255,.12)', borderRadius: 12 }}
        />
      </RadarChart>
    </ResponsiveContainer>
  </motion.div>
)

export default RadarAnalytics
