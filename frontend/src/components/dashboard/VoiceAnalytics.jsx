import React from 'react'
import { motion } from 'framer-motion'
import { Mic2 } from 'lucide-react'

const readValue = (analytics, keys) => {
  for (const key of keys) {
    if (analytics?.[key] !== undefined && analytics?.[key] !== null) return analytics[key]
  }
  return null
}

const VoiceAnalytics = ({ analytics = {} }) => {
  const clarity = readValue(analytics, ['clarityScore', 'clarity_score'])
  const confidence = readValue(analytics, ['confidenceLevel', 'confidence_level'])
  const bars = Array.from({ length: 18 }, (_, index) => {
    const base = Number(clarity ?? confidence ?? 35)
    return Math.max(12, Math.min(96, ((base + index * 13) % 84) + 12))
  })

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="rounded-2xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-2xl"
    >
      <div className="mb-5 flex items-center justify-between">
        <h3 className="text-xl font-semibold text-white">Voice Analytics</h3>
        <div className="rounded-xl border border-neon-purple/30 bg-neon-purple/10 p-2 text-violet-300">
          <Mic2 className="h-5 w-5" />
        </div>
      </div>
      <div className="mb-5 flex h-24 items-center gap-2 rounded-2xl border border-white/10 bg-black/20 px-4">
        {bars.map((height, index) => (
          <motion.div
            key={index}
            className="flex-1 rounded-full bg-gradient-to-t from-neon-purple to-neon-cyan"
            initial={{ height: 8 }}
            animate={{ height: `${height}%` }}
            transition={{ duration: 0.8, delay: index * 0.025 }}
          />
        ))}
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <VoiceMetric label="Speaking Speed" value={readValue(analytics, ['speakingSpeed', 'speaking_speed'])} />
        <VoiceMetric label="Pauses" value={readValue(analytics, ['pauses', 'pause_count'])} />
        <VoiceMetric label="Filler Words" value={readValue(analytics, ['fillerWords', 'filler_words'])} />
        <VoiceMetric label="Clarity Score" value={clarity !== null ? `${Math.round(clarity)}%` : null} />
        <VoiceMetric label="Confidence Level" value={confidence !== null ? `${Math.round(confidence)}%` : null} />
      </div>
    </motion.div>
  )
}

const VoiceMetric = ({ label, value }) => (
  <div className="rounded-xl border border-white/10 bg-black/20 p-4">
    <p className="text-xs uppercase tracking-[0.18em] text-gray-500">{label}</p>
    <p className="mt-3 text-lg font-semibold text-white">{value ?? 'Not captured'}</p>
  </div>
)

export default VoiceAnalytics
