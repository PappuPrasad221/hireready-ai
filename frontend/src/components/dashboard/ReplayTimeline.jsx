import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Pause, Play, RotateCcw } from 'lucide-react'

const ReplayTimeline = ({ items }) => {
  const [playing, setPlaying] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="rounded-2xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-2xl"
    >
      <div className="mb-5 flex items-center justify-between gap-4">
        <h3 className="text-xl font-semibold text-white">Replay Timeline</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setPlaying((value) => !value)}
            className="rounded-xl border border-neon-blue/30 bg-neon-blue/10 p-2 text-neon-cyan transition hover:bg-neon-blue/20"
            aria-label={playing ? 'Pause replay' : 'Play replay'}
          >
            {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </button>
          <button
            onClick={() => setPlaying(false)}
            className="rounded-xl border border-white/10 bg-white/[0.04] p-2 text-gray-300 transition hover:text-white"
            aria-label="Reset replay"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>
      </div>
      <div className="space-y-4">
        {items.length ? items.map((item, index) => (
          <div key={item.id} className="relative rounded-2xl border border-white/10 bg-black/20 p-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-neon-cyan">{item.timestamp || `Step ${index + 1}`}</p>
                <h4 className="mt-2 text-sm font-semibold text-white">{item.round}</h4>
              </div>
              <div className="rounded-full border border-neon-purple/30 bg-neon-purple/10 px-3 py-1 text-sm text-violet-200">
                {item.score ?? '--'}%
              </div>
            </div>
            <div className="mt-4 grid gap-3 text-sm text-gray-400 md:grid-cols-3">
              <p><span className="text-gray-200">Question:</span> {item.questionText}</p>
              <p><span className="text-gray-200">Answer:</span> {item.answer}</p>
              <p><span className="text-gray-200">AI Evaluation:</span> {item.feedback?.detailed_feedback || item.feedback?.summary || 'Feedback not captured.'}</p>
            </div>
            {playing && (
              <motion.div
                className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-neon-blue to-neon-purple"
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ duration: 1.5, repeat: Infinity }}
              />
            )}
          </div>
        )) : (
          <p className="rounded-xl border border-white/10 bg-black/20 p-4 text-gray-400">
            Replay events were not included in this report.
          </p>
        )}
      </div>
    </motion.div>
  )
}

export default ReplayTimeline
