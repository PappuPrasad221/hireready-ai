import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, Brain } from 'lucide-react'

const list = (value) => {
  if (!value) return []
  return Array.isArray(value) ? value.filter(Boolean) : [value]
}

const QuestionAnalysisCard = ({ item, onExplain }) => {
  const [open, setOpen] = useState(false)
  const feedback = item.feedback || {}
  const strengths = list(feedback.strengths || feedback.covered_points)
  const weaknesses = list(feedback.weaknesses)
  const missing = list(feedback.missing_points || feedback.missingPoints)
  const improved = feedback.improved_answer || feedback.suggested_answer || feedback.suggestedAnswer

  return (
    <motion.div layout className="rounded-2xl border border-white/10 bg-black/20 p-4">
      <button className="flex w-full items-start justify-between gap-4 text-left" onClick={() => setOpen((value) => !value)}>
        <div>
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-neon-blue/30 bg-neon-blue/10 px-3 py-1 text-xs text-neon-cyan">
              Q{item.index} - {item.round}
            </span>
            <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-gray-300">
              {item.score ?? '--'}%
            </span>
          </div>
          <h4 className="text-base font-semibold leading-7 text-white">{item.questionText}</h4>
        </div>
        <ChevronDown className={`mt-1 h-5 w-5 shrink-0 text-gray-400 transition ${open ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="mt-5 space-y-4 border-t border-white/10 pt-5">
              <div>
                <p className="mb-2 text-xs uppercase tracking-[0.2em] text-gray-500">Transcript</p>
                <p className="rounded-xl bg-white/[0.04] p-4 text-sm leading-6 text-gray-300">{item.answer}</p>
              </div>
              <div className="grid gap-3 md:grid-cols-3">
                <InsightBlock title="Strengths" items={strengths} tone="text-emerald-300" />
                <InsightBlock title="Weaknesses" items={weaknesses} tone="text-rose-300" />
                <InsightBlock title="Missing Points" items={missing} tone="text-amber-300" />
              </div>
              {improved && (
                <div>
                  <p className="mb-2 text-xs uppercase tracking-[0.2em] text-gray-500">Improved Answer</p>
                  <p className="rounded-xl border border-neon-purple/20 bg-neon-purple/10 p-4 text-sm leading-6 text-gray-300">
                    {improved}
                  </p>
                </div>
              )}
              <button
                onClick={onExplain}
                className="inline-flex items-center rounded-xl border border-neon-blue/30 bg-neon-blue/10 px-4 py-3 text-sm font-semibold text-neon-cyan transition hover:border-neon-blue/60 hover:bg-neon-blue/20"
              >
                <Brain className="mr-2 h-4 w-4" />
                View Deep Explanation
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

const InsightBlock = ({ title, items, tone }) => (
  <div className="rounded-xl border border-white/10 bg-white/[0.035] p-4">
    <h5 className={`mb-3 text-sm font-semibold ${tone}`}>{title}</h5>
    {items.length ? (
      <ul className="space-y-2 text-sm text-gray-400">
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    ) : (
      <p className="text-sm text-gray-500">Not captured.</p>
    )}
  </div>
)

export default QuestionAnalysisCard
