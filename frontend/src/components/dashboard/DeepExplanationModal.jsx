import React from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { X } from 'lucide-react'

const getDeep = (item) => {
  const feedback = item?.feedback || {}
  const deep = feedback.deep_explanation || feedback.deepExplanation || {}
  return {
    userAnswered: deep.what_user_answered || item?.answer,
    expected: deep.what_interviewer_expected || feedback.expected_answer || feedback.expected_points,
    missing: deep.what_was_missing || feedback.missing_points,
    structure: deep.ideal_answer_structure || feedback.ideal_structure,
    improved: deep.improved_answer || feedback.improved_answer || feedback.suggested_answer
  }
}

const normalize = (value) => {
  if (!value) return 'Not captured in this report.'
  if (Array.isArray(value)) return value.join(', ')
  return value
}

const DeepExplanationModal = ({ item, onClose }) => {
  const deep = getDeep(item)

  return (
    <AnimatePresence>
      {item && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xl"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            initial={{ scale: 0.94, y: 24 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.94, y: 24 }}
            className="max-h-[88vh] w-full max-w-4xl overflow-y-auto rounded-2xl border border-white/10 bg-[#090b16] p-6 shadow-[0_0_80px_rgba(0,212,255,.18)]"
          >
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.22em] text-neon-cyan">Deep explanation</p>
                <h3 className="mt-2 text-2xl font-bold text-white">{item.questionText}</h3>
              </div>
              <button onClick={onClose} className="rounded-xl border border-white/10 bg-white/[0.04] p-2 text-gray-300 hover:text-white">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <DeepBlock title="What user answered" value={deep.userAnswered} />
              <DeepBlock title="What interviewer expected" value={deep.expected} />
              <DeepBlock title="What was missing" value={deep.missing} />
              <DeepBlock title="Better answer structure" value={deep.structure} />
            </div>
            <div className="mt-4 rounded-2xl border border-neon-purple/20 bg-neon-purple/10 p-5">
              <h4 className="mb-3 text-sm font-semibold text-violet-200">Ideal answer example</h4>
              <p className="leading-7 text-gray-300">{normalize(deep.improved)}</p>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

const DeepBlock = ({ title, value }) => (
  <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-5">
    <h4 className="mb-3 text-sm font-semibold text-neon-cyan">{title}</h4>
    <p className="leading-7 text-gray-300">{normalize(value)}</p>
  </div>
)

export default DeepExplanationModal
