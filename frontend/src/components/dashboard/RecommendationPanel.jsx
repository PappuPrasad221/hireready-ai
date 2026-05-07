import React from 'react'
import { motion } from 'framer-motion'
import { Award, Map, Target } from 'lucide-react'

const inferRecommendation = (label, score) => {
  if (label) return label
  if (score === null || score === undefined) return 'Not captured'
  if (score >= 85) return 'Strong Hire'
  if (score >= 70) return 'Hire'
  if (score >= 55) return 'Average'
  return 'Needs Improvement'
}

const RecommendationPanel = ({ recommendation, overallScore }) => {
  const label = inferRecommendation(recommendation.label, overallScore)

  return (
    <motion.aside
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      className="rounded-2xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-2xl"
    >
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-neon-cyan">Final result</p>
          <h3 className="mt-2 text-3xl font-black text-white">{label}</h3>
        </div>
        <div className="rounded-2xl border border-neon-blue/30 bg-neon-blue/10 p-3 text-neon-cyan">
          <Award className="h-7 w-7" />
        </div>
      </div>
      <PanelList icon={Map} title="Improvement Roadmap" items={recommendation.roadmap} />
      <PanelList icon={Target} title="Suggested Learning Topics" items={recommendation.learningTopics} />
      <PanelList icon={Target} title="Practice Areas" items={recommendation.practiceAreas} />
    </motion.aside>
  )
}

const PanelList = ({ icon: Icon, title, items }) => (
  <div className="mt-4 rounded-xl border border-white/10 bg-black/20 p-4">
    <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
      <Icon className="h-4 w-4 text-neon-cyan" />
      {title}
    </div>
    {items?.length ? (
      <ul className="space-y-2 text-sm leading-6 text-gray-400">
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    ) : (
      <p className="text-sm text-gray-500">Not captured in this report.</p>
    )}
  </div>
)

export default RecommendationPanel
